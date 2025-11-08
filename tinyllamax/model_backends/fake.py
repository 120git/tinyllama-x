"""Fake backend for local demos and tests.

Returns a provided JSON string verbatim if given; otherwise uses simple
heuristics to turn user text into a minimal intent JSON.
"""
from __future__ import annotations

import json
from typing import Optional

from .interface import ModelBackend


class FakeBackend(ModelBackend):
    def __init__(self, forced_json: Optional[str] = None) -> None:
        self.forced_json = forced_json

    def complete(self, system: str, user: str) -> str:
        if self.forced_json:
            return self.forced_json
        # Heuristic fallback: very small rules to create a plausible intent
        u = user.strip().lower()
        if u.startswith("install "):
            pkg = u.split(maxsplit=1)[1]
            return json.dumps({"intent": "InstallPackage", "package": pkg})
        if u.startswith("remove ") or u.startswith("uninstall "):
            pkg = u.split(maxsplit=1)[1]
            return json.dumps({"intent": "RemovePackage", "package": pkg})
        if u.startswith("search ") or "search for" in u:
            q = u.replace("search for", "search ", 1) if "search for" in u else u
            q = q.split(maxsplit=1)[1]
            return json.dumps({"intent": "SearchPackage", "query": q})
        if "what does" in u or u.startswith("explain "):
            if u.startswith("explain "):
                cmd = u.split(maxsplit=1)[1]
            else:
                # pattern: "what does <cmd> do" or "what does <cmd> do?"
                segment = u.split("what does", 1)[1].strip()
                segment = segment.replace("?", "")
                if segment.endswith(" do"):
                    segment = segment[:-3].strip()
                cmd = segment.split()[0] if segment else "ls"
            return json.dumps({"intent": "ExplainCommand", "command": cmd})
        if "update" in u and "upgrade" not in u:
            return json.dumps({"intent": "UpdateSystem"})
        if "upgrade" in u:
            return json.dumps({"intent": "UpgradeSystem"})
        if "distro" in u or "distribution" in u:
            return json.dumps({"intent": "DetectDistro"})
        # Fallback
        return json.dumps({"intent": "ExplainCommand", "command": "ls"})


__all__ = ["FakeBackend"]
