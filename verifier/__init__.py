import json
from dataclasses import asdict
from pathlib import Path

from contract import Task, Tool

from .oracle import expected, input_problem


def result(valid, message):
    return {"valid": valid, "score": float(valid), "message": message, "details": {}}


def verify_input(tool, value):
    problem = input_problem(value) if Tool(tool) == Tool.COMPUTE else None
    return result(problem is None, problem or "input valid")


def saved(output, workspace):
    if output.path != "result.json":
        return False
    path = Path(workspace) / "result.json"
    if not path.is_file() or path.is_symlink():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return json.dumps(data, sort_keys=True) == json.dumps(
            asdict(output.result), sort_keys=True, default=lambda v: v.value
        )
    except (ValueError, OSError):
        return False


def verify_output(tool, input_value, output_value, workspace):
    if Tool(tool) == Tool.SAVE:
        valid = output_value.result == input_value.result and saved(output_value, workspace)
    else:
        valid = input_problem(input_value) is None and output_value == expected(input_value)
    return result(valid, "output verified" if valid else "output mismatch or missing artifact")


def verify_task(task, arguments, output, reference, workspace):
    Task(task)
    valid = input_problem(arguments) is None and output.result == expected(arguments) and saved(output, workspace)
    return result(valid, "task verified" if valid else "task mismatch or missing artifact")
