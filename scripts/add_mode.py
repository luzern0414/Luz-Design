#!/usr/bin/env python3
"""Safely activate another mode in an existing Luz Design session."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from new_session import MODE_NAMES, OTHER_SKILL_MODES, OUTPUT_ROOT, SESSION_RE, SKILL_ROOT, init_mode

LOCK_TIMEOUT_SECONDS = 5.0


def load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain an object")
    return data


def atomic_json(path: Path, data: dict) -> None:
    if path.is_symlink():
        raise ValueError(f"refusing to replace symlink: {path}")
    temp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def acquire_lock(lock: Path) -> None:
    deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
    while True:
        try:
            lock.mkdir()
            return
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"timed out waiting for manifest lock: {lock}")
            time.sleep(0.05)


def checked_session(root: Path, session: Path) -> Path:
    root = root.resolve()
    candidate = session.resolve()
    if candidate.parent != root or not SESSION_RE.match(candidate.name) or not candidate.is_dir():
        raise ValueError("session must be an existing numbered directory directly under the output root")
    return candidate


def add_mode(root: Path, session: Path, mode: str, *, standalone_poster: bool = False, skill_root: Path = SKILL_ROOT) -> dict:
    if mode in OTHER_SKILL_MODES:
        raise ValueError(f"{mode} belongs to {OTHER_SKILL_MODES[mode]}, not Luz-Design; use that skill")
    if mode not in MODE_NAMES:
        raise ValueError(f"add_mode supports {' or '.join(MODE_NAMES)}")
    session = checked_session(root, session)
    work = session / "raw"
    manifest_path = work / "99-delivery" / "MANIFEST.json"
    approvals_path = work / "99-delivery" / "APPROVALS.json"
    manifest = load_json(manifest_path)
    approvals = load_json(approvals_path)
    modes = list(manifest.get("modes", []))
    kind = manifest.get("session_kind")
    if mode == "visual":
        from validate_session import validate
        poster_requested = (
            standalone_poster
            and kind == "standalone_poster"
            and approvals.get("standalone_poster", {}).get("status") in {"requested", "approved"}
        )
        if not poster_requested:
            raise PermissionError("visual mode is standalone visual work and must be declared with --standalone-poster when the session is created; product visuals belong to Luz-System")
        errors = validate(session)
        if errors:
            raise PermissionError("standalone poster gate failed: " + "; ".join(errors))

    if mode in modes:
        return manifest

    init_mode(skill_root, work, mode)
    updated_modes = [item for item in MODE_NAMES if item in set(modes + [mode])]
    lock = manifest_path.with_name(".MANIFEST.lock")
    acquire_lock(lock)
    try:
        current = load_json(manifest_path)
        if current.get("session_id") != manifest.get("session_id"):
            raise ValueError("manifest changed during update")
        current_modes = list(current.get("modes", []))
        if mode not in current_modes:
            current_modes.append(mode)
        current["modes"] = [item for item in MODE_NAMES if item in set(current_modes)]
        atomic_json(manifest_path, current)
        return current
    finally:
        try:
            lock.rmdir()
        except FileNotFoundError:
            pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Activate visual (standalone poster sessions only) or document mode in an existing session.")
    parser.add_argument("session", help="Numbered session folder")
    parser.add_argument("mode", choices=list(MODE_NAMES))
    parser.add_argument("--standalone-poster", action="store_true")
    parser.add_argument("--root", help="Session root override, primarily for tests")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve() if args.root else OUTPUT_ROOT
    try:
        manifest = add_mode(root, Path(args.session), args.mode, standalone_poster=args.standalone_poster)
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print("PASS: active modes: " + ", ".join(manifest.get("modes", [])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
