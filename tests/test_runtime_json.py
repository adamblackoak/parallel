from app.runtime import _extract_json


def test_extract_json_accepts_plain_object():
    payload = _extract_json('{"overall_status":"GO","findings":[]}')
    assert payload["overall_status"] == "GO"


def test_extract_json_accepts_fenced_object():
    payload = _extract_json('```json\n{"overall_status":"VERIFY","findings":[]}\n```')
    assert payload["overall_status"] == "VERIFY"


def test_extract_json_fails_conservatively():
    payload = _extract_json("not json")
    assert payload["overall_status"] == "VERIFY"
    assert payload["raw_response"] == "not json"
