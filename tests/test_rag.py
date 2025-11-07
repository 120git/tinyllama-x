import types
import builtins

import tinyllamax.core.rag as rag


class DummyProc:
    def __init__(self, stdout: str = "", stderr: str = "", returncode: int = 0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def test_tldr_success(monkeypatch):
    def fake_run(args, **kwargs):
        assert args[:1] == ["tldr"]
        assert args[1] == "ls"
        return DummyProc(stdout="# TLDR for ls\nList directory contents", returncode=0)

    monkeypatch.setattr(rag.subprocess, "run", fake_run)
    out = rag.tldr("ls -la /tmp")
    assert "TLDR for ls" in out


def test_tldr_not_installed(monkeypatch):
    def fake_run(args, **kwargs):
        raise FileNotFoundError("tldr not found")

    monkeypatch.setattr(rag.subprocess, "run", fake_run)
    out = rag.tldr("ls -la")
    assert out == ""


def test_man_snippet_success(monkeypatch):
    long_text = "LS(1)\nNAME\n ls - list directory contents\n" + ("x" * 1000)

    def fake_run(args, **kwargs):
        assert args[0] == "man"
        # ensure pager/env applied by presence in kwargs
        assert kwargs.get("env", {}).get("PAGER") == "cat"
        return DummyProc(stdout=long_text, returncode=0)

    monkeypatch.setattr(rag.subprocess, "run", fake_run)
    out = rag.man_snippet("ls -la", max_chars=120)
    assert out.startswith("LS(1)")
    assert len(out) <= 120


def test_man_not_installed(monkeypatch):
    def fake_run(args, **kwargs):
        raise FileNotFoundError("man not found")

    monkeypatch.setattr(rag.subprocess, "run", fake_run)
    out = rag.man_snippet("ls")
    assert out == ""


def test_explain_merge(monkeypatch):
    calls = []

    def fake_run(args, **kwargs):
        if args[0] == "tldr":
            calls.append("tldr")
            return DummyProc(stdout="TLDR content", returncode=0)
        else:
            calls.append("man")
            return DummyProc(stdout="MAN content", returncode=0)

    monkeypatch.setattr(rag.subprocess, "run", fake_run)
    out = rag.explain_command("ls")
    assert "TLDR" in out and "Man snippet" in out
    assert calls == ["tldr", "man"]


def test_explain_fallback(monkeypatch):
    def fake_run(args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(rag.subprocess, "run", fake_run)
    out = rag.explain_command("ls")
    assert "No explanation" in out
