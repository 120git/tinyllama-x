"""Smoke tests ensuring modules import and basic objects instantiate."""
import importlib

MODULES = [
    "tinyllamax",
    "tinyllamax.config",
    "tinyllamax.models",
    "tinyllamax.cli",
]

def test_imports():
    for name in MODULES:
        m = importlib.import_module(name)
        assert m is not None


def test_settings_instance():
    from tinyllamax.config import AppSettings
    s = AppSettings()
    assert hasattr(s, "model_path")


def test_domain_models():
    from tinyllamax.models import PackageAction, CommandExplain
    pa = PackageAction(action="install", packages=["htop"])  # type: ignore[arg-type]
    ce = CommandExplain(command="ls -la", detail_level=2)
    assert pa.action == "install"
    assert ce.detail_level == 2
