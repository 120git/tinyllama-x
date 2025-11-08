from tinyllamax.model_backends.fake import FakeBackend
from tinyllamax.core.model import IntentDecider
from tinyllamax.core.intents import InstallPackage, SearchPackage, ExplainCommand

class DummyBackend(FakeBackend):
    pass


def test_fake_forced_json():
    be = FakeBackend(forced_json='{"intent":"InstallPackage","package":"htop"}')
    intent = IntentDecider(be).decide("anything")
    assert isinstance(intent, InstallPackage)
    assert intent.package == "htop"


def test_fake_install_heuristic():
    be = FakeBackend()
    intent = IntentDecider(be).decide("install git")
    assert isinstance(intent, InstallPackage)
    assert intent.package == "git"


def test_fake_search_heuristic():
    be = FakeBackend()
    intent = IntentDecider(be).decide("search for curl")
    assert isinstance(intent, SearchPackage)
    assert intent.query == "curl"


def test_fake_explain_fallback():
    be = FakeBackend()
    intent = IntentDecider(be).decide("what does ls do?")
    assert isinstance(intent, ExplainCommand)
    assert intent.command == "ls"
