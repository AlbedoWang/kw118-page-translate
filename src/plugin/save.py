import json
from dataclasses import asdict

from contract import SaveOutput


def save_result(value, workspace):
    workspace.mkdir(parents=True, exist_ok=True)
    destination = workspace / "result.json"
    if destination.is_symlink():
        raise ValueError("result.json must not be a symlink")
    destination.write_text(
        json.dumps(asdict(value.result), sort_keys=True, default=lambda v: v.value), encoding="utf-8"
    )
    return SaveOutput("result.json", value.result)
