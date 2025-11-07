import json
import tinyllamax.core.model as model
from tinyllamax.model_backends.interface import ModelBackend
from tinyllamax.core.intents import InstallPackage, SearchPackage, parse_intent


class FakeBackend(ModelBackend):
    def __init__(self, payload: str) -> None:
        self.payload = payload

    def complete(self, system: str, user: str) -> str:  # pragma: no cover - trivial
        return self.payload


def test_decider_parses_raw_json():
    payload = json.dumps({"intent": "InstallPackage", "package": "htop"})
    decider = model.IntentDecider(FakeBackend(payload))
    intent = decider.decide("install htop")
    assert isinstance(intent, InstallPackage)
    assert intent.package == "htop"


def test_decider_parses_fenced_json():
    payload = """
```json
{"intent":"SearchPackage","query":"neovim"}
```
"""
    decider = model.IntentDecider(FakeBackend(payload))
    intent = decider.decide("search neovim")
    assert isinstance(intent, SearchPackage)
    assert intent.query == "neovim"


def test_decider_picks_first_object_in_noisy_output():
    payload = 'some preface {"intent":"InstallPackage","package":"git"} trailing text {"ignore":true}'
    decider = model.IntentDecider(FakeBackend(payload))
    intent = decider.decide("install git")
    assert isinstance(intent, InstallPackage)
    assert intent.package == "git"
