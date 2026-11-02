import json
from copy import deepcopy
from pathlib import Path

import pytest
from slimconfig import build_output, plain_output

import verifier
from contract import ComputeInput, ComputeOutput, SaveInput, SaveOutput, Task, Tool
from plugin import compute, save_result

CASES = json.loads(Path(__file__).with_name("cases.json").read_text())
INVALID = json.loads(Path(__file__).with_name("invalid.json").read_text())


@pytest.mark.parametrize("raw", CASES)
def test_complete_result_and_rejection(raw, tmp_path):
    value = build_output(raw, ComputeInput)
    assert verifier.verify_input(Tool.COMPUTE.value, value)["valid"]
    made = compute(value, tmp_path)
    assert verifier.verify_output(Tool.COMPUTE.value, value, made, tmp_path)["valid"]
    saved = save_result(SaveInput(made), tmp_path)
    submitted = build_output(plain_output(saved), SaveOutput)
    verdict = verifier.verify_task(Task.RUN.value, value, submitted, None, tmp_path)
    assert verdict["valid"], verdict
    assert verdict == verifier.verify_task(Task.RUN.value, value, submitted, None, tmp_path)
    assert verifier.verify_output(Tool.SAVE.value, SaveInput(made), submitted, tmp_path)["valid"]
    wrong_path = SaveOutput("elsewhere.json", made)
    assert not verifier.verify_task(Task.RUN.value, value, wrong_path, None, tmp_path)["valid"]
    data = plain_output(made)
    for field, original in data.items():
        changed = deepcopy(data)
        if isinstance(original, bool):
            changed[field] = not original
        elif isinstance(original, int):
            changed[field] = original + 1
        elif isinstance(original, str):
            changed[field] = original + "x"
        elif original:
            changed[field] = original[:-1]
        else:
            continue
        wrong = build_output(changed, ComputeOutput)
        (tmp_path / "result.json").write_text(json.dumps(changed))
        assert not verifier.verify_output(Tool.COMPUTE.value, value, wrong, tmp_path)["valid"]
        assert not verifier.verify_task(Task.RUN.value, value, SaveOutput("result.json", wrong), None, tmp_path)[
            "valid"
        ]
    (tmp_path / "result.json").write_text("{")
    assert not verifier.verify_task(Task.RUN.value, value, submitted, None, tmp_path)["valid"]
    (tmp_path / "result.json").unlink()
    assert not verifier.verify_task(Task.RUN.value, value, submitted, None, tmp_path)["valid"]
    # Contract validation must reject missing and wrongly typed fields before the verifier.
    missing = dict(raw)
    missing.pop(next(iter(missing)))
    with pytest.raises((TypeError, ValueError)):
        build_output(missing, ComputeInput)
    with pytest.raises((TypeError, ValueError)):
        build_output({"path": [], "result": data}, SaveOutput)


@pytest.mark.parametrize("raw", INVALID)
def test_invalid_input(raw, tmp_path):
    value = build_output(raw, ComputeInput)
    assert not verifier.verify_input(Tool.COMPUTE.value, value)["valid"]
    with pytest.raises(ValueError):
        compute(value, tmp_path)


def test_symlink_not_written(tmp_path):
    outside = tmp_path / "outside.json"
    outside.write_text("untouched")
    (tmp_path / "result.json").symlink_to(outside)
    result = compute(build_output(CASES[0], ComputeInput), tmp_path)
    with pytest.raises(ValueError):
        save_result(SaveInput(result), tmp_path)
    assert outside.read_text() == "untouched"
