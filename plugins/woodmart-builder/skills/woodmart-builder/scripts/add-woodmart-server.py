#!/usr/bin/env python3
"""
add-woodmart-server.py - safely add a WoodMart (WordPress MCP Adapter) server to
Claude Desktop and, optionally, Claude Code.

  * finds claude_desktop_config.json per OS (macOS / Windows incl. Microsoft Store / Linux)
  * backs it up first (<file>.bak-YYYYMMDD-HHMMSS)
  * MERGES into "mcpServers" - other servers and keys are kept
  * never overwrites another site's entry
  * validates the JSON and writes atomically
  * never prints the password

Input (one of):
  --from-file PATH   JSON you received: {"mcpServers": {"woodmart": {...}}} or a single server object
  --stdin            same JSON piped on stdin
  --interactive      prompts for URL and username; password is read hidden

Examples:
  python add-woodmart-server.py --from-file ~/Downloads/site-mcp.json --dry-run
  python add-woodmart-server.py --from-file ~/Downloads/site-mcp.json --claude-code
  python add-woodmart-server.py --interactive --name woodmart-northwind
"""
from __future__ import annotations

import argparse
import getpass
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from urllib.parse import urlparse

BRIDGE_COMMAND = "npx"
BRIDGE_ARGS = ["-y", "@automattic/mcp-wordpress-remote@latest"]
ENDPOINT_SUFFIX = "/mcp-adapter-default-server"
SECOND_LEVEL = {"co", "com", "net", "org", "gov", "edu", "ac"}


class UserError(Exception):
    """Expected problem - message is safe to print (never contains secrets)."""


# ---------------------------------------------------------------- helpers

def mask(value: str) -> str:
    return "********" if value else "(empty)"


def desktop_config_candidates() -> list[str]:
    home = os.path.expanduser("~")
    if sys.platform == "darwin":
        return [os.path.join(home, "Library", "Application Support", "Claude", "claude_desktop_config.json")]
    if os.name == "nt":
        paths = []
        appdata = os.environ.get("APPDATA")
        if appdata:
            paths.append(os.path.join(appdata, "Claude", "claude_desktop_config.json"))
        local = os.environ.get("LOCALAPPDATA")
        if local:
            paths += glob.glob(os.path.join(local, "Packages", "Claude_*", "LocalCache",
                                            "Roaming", "Claude", "claude_desktop_config.json"))
        return paths
    xdg = os.environ.get("XDG_CONFIG_HOME") or os.path.join(home, ".config")
    return [os.path.join(xdg, "Claude", "claude_desktop_config.json")]


def resolve_desktop_config(explicit: str | None) -> str:
    if explicit:
        return os.path.abspath(os.path.expanduser(explicit))
    candidates = desktop_config_candidates()
    if not candidates:
        raise UserError("Could not determine the Claude Desktop config location; pass --config-path.")
    existing = [p for p in candidates if os.path.isfile(p)]
    if len(existing) > 1:
        raise UserError("Found more than one Claude Desktop config:\n  " + "\n  ".join(existing)
                        + "\nRe-run with --config-path pointing at the one your Claude app uses.")
    return existing[0] if existing else candidates[0]


def derive_name(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    if not host:
        raise UserError("WP_API_URL has no valid host.")
    labels = [l for l in host.split(".") if l]
    if labels and labels[0] == "www":
        labels = labels[1:]
    if len(labels) > 1:
        labels = labels[:-1]                       # drop TLD
        if len(labels) > 1 and labels[-1] in SECOND_LEVEL:
            labels = labels[:-1]                   # drop co. in .co.uk etc.
    slug = re.sub(r"[^a-z0-9-]+", "-", "-".join(labels)).strip("-")
    if not slug:
        raise UserError("Could not derive a name from the URL; pass --name.")
    return "woodmart-" + slug


def validate_name(name: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", name):
        raise UserError("Server name must be letters, digits, '-' or '_' (max 64 chars).")
    return name


def extract_server(data: object, source_key: str | None) -> tuple[str | None, dict]:
    """Accept {"mcpServers": {...}}, {"name": {...}} or a bare server object."""
    if not isinstance(data, dict):
        raise UserError("Config must be a JSON object.")
    if "command" in data or "env" in data:
        return None, data
    servers = data.get("mcpServers", data)
    if not isinstance(servers, dict) or not servers:
        raise UserError("No servers found in the config.")
    if source_key:
        if source_key not in servers:
            raise UserError(f"Server '{source_key}' not found. Available: {', '.join(servers)}")
        return source_key, servers[source_key]
    if len(servers) > 1:
        raise UserError("Config contains several servers (" + ", ".join(servers)
                        + "); choose one with --source-key.")
    key = next(iter(servers))
    return key, servers[key]


def normalize_server(server: dict) -> dict:
    if not isinstance(server, dict):
        raise UserError("Server entry must be a JSON object.")
    env = server.get("env") or {}
    url = str(env.get("WP_API_URL", "")).strip()
    user = str(env.get("WP_API_USERNAME", "")).strip()
    pwd = str(env.get("WP_API_PASSWORD", ""))
    missing = [k for k, v in (("WP_API_URL", url), ("WP_API_USERNAME", user), ("WP_API_PASSWORD", pwd)) if not v]
    if missing:
        raise UserError("Missing in env: " + ", ".join(missing))
    if (pwd.strip().startswith("<") or "application password" in pwd.lower()
            or re.fullmatch(r"[xX\s]+", pwd)):
        raise UserError("WP_API_PASSWORD still looks like a placeholder.")
    host = (urlparse(url).hostname or "").lower()
    if host in {"example.com", "www.example.com", "domain", "domain.com"}:
        raise UserError("WP_API_URL still points at the placeholder domain.")
    out = dict(server)
    out.setdefault("command", BRIDGE_COMMAND)
    out.setdefault("args", list(BRIDGE_ARGS))
    out["env"] = dict(env, WP_API_URL=url, WP_API_USERNAME=user, WP_API_PASSWORD=pwd)
    return out


def check_url(url: str) -> list[str]:
    warnings = []
    p = urlparse(url)
    if p.scheme != "https":
        warnings.append("WP_API_URL is not https:// - Application Passwords require HTTPS.")
    if not p.path.rstrip("/").endswith(ENDPOINT_SUFFIX):
        warnings.append(f"WP_API_URL usually ends with /wp-json/mcp{ENDPOINT_SUFFIX}.")
    return warnings


def same_site(a: dict, b: dict) -> bool:
    ua = str((a.get("env") or {}).get("WP_API_URL", "")).rstrip("/").lower()
    ub = str((b.get("env") or {}).get("WP_API_URL", "")).rstrip("/").lower()
    return bool(ua) and ua == ub


def read_input(args) -> dict:
    if args.interactive:
        if not sys.stdin.isatty():
            raise UserError("--interactive needs a real terminal; use --from-file or --stdin instead.")
        url = input("WP_API_URL (https://domain/wp-json/mcp/mcp-adapter-default-server): ").strip()
        user = input("WP_API_USERNAME: ").strip()
        pwd = getpass.getpass("WP_API_PASSWORD (application password, hidden): ")
        return {"command": BRIDGE_COMMAND, "args": list(BRIDGE_ARGS),
                "env": {"WP_API_URL": url, "WP_API_USERNAME": user, "WP_API_PASSWORD": pwd}}
    if args.stdin:
        raw = sys.stdin.read()
    else:
        path = os.path.expanduser(args.from_file)
        if not os.path.isfile(path):
            raise UserError(f"File not found: {path}")
        with open(path, "r", encoding="utf-8-sig") as fh:
            raw = fh.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        # position only - never echo the content
        raise UserError(f"Input is not valid JSON (line {exc.lineno}, column {exc.colno}).") from None
    return extract_server(data, args.source_key)[1]


# ---------------------------------------------------------------- Claude Desktop

def add_to_desktop(path: str, name: str, server: dict, replace: bool, dry_run: bool) -> None:
    config: dict = {}
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8-sig") as fh:
            text = fh.read()
        if text.strip():
            try:
                config = json.loads(text)
            except json.JSONDecodeError as exc:
                raise UserError(f"Existing config is not valid JSON (line {exc.lineno}, column "
                                f"{exc.colno}). Fix it first; nothing was changed.") from None
        if not isinstance(config, dict):
            raise UserError("Existing config is not a JSON object; nothing was changed.")

    servers = config.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        raise UserError('"mcpServers" in the existing config is not an object; nothing was changed.')

    for other_name, other in servers.items():
        if other_name != name and isinstance(other, dict) and same_site(other, server):
            print(f"  note: server '{other_name}' already points at this same URL.")

    if name in servers:
        if not same_site(servers[name], server):
            raise UserError(f"'{name}' already exists for a DIFFERENT site. Choose another --name; "
                            "the existing entry was not touched.")
        if not replace:
            raise UserError(f"'{name}' already exists for this site. Re-run with --replace to update it.")

    servers[name] = server
    new_text = json.dumps(config, indent=2, ensure_ascii=False) + "\n"
    json.loads(new_text)  # validate round-trip

    print(f"  Claude Desktop config: {path}")
    print(f"  servers after merge  : {', '.join(servers)}")
    if dry_run:
        print("  dry run - nothing written.")
        return

    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.isfile(path):
        stamp = f"{path}.bak-{datetime.now():%Y%m%d-%H%M%S}"
        backup, n = stamp, 1
        while os.path.exists(backup):          # never overwrite an earlier backup
            backup, n = f"{stamp}-{n}", n + 1
        shutil.copy2(path, backup)
        print(f"  backup               : {backup}")
    fd, tmp = tempfile.mkstemp(prefix=".claude_desktop_config.", suffix=".tmp", dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(new_text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    with open(path, "r", encoding="utf-8") as fh:
        if name not in json.load(fh).get("mcpServers", {}):
            raise UserError("Verification failed after write; restore the backup.")
    print("  written and verified.")


# ---------------------------------------------------------------- Claude Code

def add_to_claude_code(name: str, server: dict, replace: bool, dry_run: bool) -> None:
    exe = shutil.which("claude")
    if not exe:
        raise UserError("Claude Code CLI ('claude') not found on PATH; skipped Claude Code.")
    run = lambda argv: subprocess.run([exe, *argv], capture_output=True, text=True)  # noqa: E731
    # output of `mcp get` may include env values - capture it and never print it
    exists = run(["mcp", "get", name]).returncode == 0
    if exists and not replace:
        raise UserError(f"Claude Code already has a server named '{name}'. Use --replace to update it.")
    if dry_run:
        print(f"  Claude Code: would {'replace' if exists else 'add'} '{name}' (scope user). dry run.")
        return
    if exists:
        run(["mcp", "remove", name, "--scope", "user"])
    payload = json.dumps({"type": "stdio", "command": server["command"],
                          "args": server.get("args", []), "env": server["env"]})
    res = run(["mcp", "add-json", name, payload, "--scope", "user"])
    if res.returncode != 0:
        raise UserError("'claude mcp add-json' failed (exit "
                        f"{res.returncode}). Run 'claude mcp list' to check; output hidden to protect secrets.")
    print(f"  Claude Code: added '{name}' (scope user). Start a new session and check /mcp.")


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description="Add a WoodMart MCP server to Claude Desktop / Claude Code.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--from-file", help="JSON config file you received (keep it outside the repo)")
    src.add_argument("--stdin", action="store_true", help="read the JSON config from stdin")
    src.add_argument("--interactive", action="store_true", help="prompt for values (password hidden)")
    ap.add_argument("--source-key", help="server key to take from the input if it has several")
    ap.add_argument("--name", help="server key to write (default: woodmart-<domain>)")
    ap.add_argument("--config-path", help="explicit claude_desktop_config.json path")
    ap.add_argument("--replace", action="store_true", help="update an existing entry for the SAME site")
    ap.add_argument("--claude-code", action="store_true", help="also add to Claude Code (user scope)")
    ap.add_argument("--no-desktop", action="store_true", help="skip Claude Desktop")
    ap.add_argument("--dry-run", action="store_true", help="show what would change, write nothing")
    args = ap.parse_args()

    try:
        server = normalize_server(read_input(args))
        env = server["env"]
        name = validate_name(args.name or derive_name(env["WP_API_URL"]))

        print(f"Server name : {name}")
        print(f"Site URL    : {env['WP_API_URL']}")
        print(f"Username    : {env['WP_API_USERNAME']}")
        print(f"Password    : {mask(env['WP_API_PASSWORD'])}")
        for w in check_url(env["WP_API_URL"]):
            print(f"  warning: {w}")

        if not args.no_desktop:
            add_to_desktop(resolve_desktop_config(args.config_path), name, server, args.replace, args.dry_run)
        if args.claude_code:
            add_to_claude_code(name, server, args.replace, args.dry_run)

        if not args.dry_run and not args.no_desktop:
            print("\nNext: fully quit Claude Desktop (macOS Cmd+Q / Windows tray icon -> Quit) and reopen it.")
        return 0
    except UserError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\ncancelled - nothing written.", file=sys.stderr)
        return 130
    except Exception as exc:  # never dump a traceback that could include secrets
        print(f"error: unexpected {type(exc).__name__}; nothing further was written.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
