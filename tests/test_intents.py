from tinyllamax.core.intents import (
    parse_intent,
    DetectDistro,
    SearchPackage,
    InstallPackage,
    RemovePackage,
    UpdateSystem,
    UpgradeSystem,
    ExplainCommand,
    TroubleshootError,
    IntentParseError,
)


def test_parse_detect_distro():
    obj = {"intent": "DetectDistro"}
    res = parse_intent(obj)
    assert isinstance(res, DetectDistro)


def test_parse_search_package():
    obj = {"intent": "SearchPackage", "query": "htop"}
    res = parse_intent(obj)
    assert isinstance(res, SearchPackage)
    assert res.query == "htop"


def test_parse_install_remove_update_upgrade_explain_troubleshoot():
    assert isinstance(parse_intent({"intent": "InstallPackage", "package": "htop"}), InstallPackage)
    assert isinstance(parse_intent({"intent": "RemovePackage", "package": "htop"}), RemovePackage)
    assert isinstance(parse_intent({"intent": "UpdateSystem"}), UpdateSystem)
    assert isinstance(parse_intent({"intent": "UpgradeSystem"}), UpgradeSystem)
    assert isinstance(parse_intent({"intent": "ExplainCommand", "command": "ls -la"}), ExplainCommand)
    assert isinstance(parse_intent({"intent": "TroubleshootError", "error_text": "No such file or directory"}), TroubleshootError)


def test_parse_errors():
    try:
        parse_intent(123)  # type: ignore[arg-type]
    except IntentParseError as e:
        assert "Input must be a dict" in str(e)
    else:
        assert False, "Expected error"

    try:
        parse_intent({})
    except IntentParseError as e:
        assert "Missing 'intent'" in str(e)
    else:
        assert False, "Expected error"

    try:
        parse_intent({"intent": "UnknownThing"})
    except IntentParseError as e:
        assert "Unknown intent" in str(e)
    else:
        assert False, "Expected error"

    try:
        parse_intent({"intent": "InstallPackage"})
    except IntentParseError as e:
        assert "Validation failed" in str(e)
    else:
        assert False, "Expected error"
