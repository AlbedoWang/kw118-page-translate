# kw118-page-translate

An original COMP 480/580 verifiable systems task by Kaijian Wang (kw118).

## Tools

| Tool/task | Behavior |
|---|---|
| `translate_addresses` | Compute the exact typed domain result. |
| `save_result` | Accept a ComputeOutput as result; write result.json and return path plus result. |
| `page-translate` | Agent task: compute, save, then submit the saved output unchanged. |

### Rules and output semantics

page_size, virtual_pages and frames are positive integers. Each entry has page, resident, frame and writable. Virtual pages are unique and in range. Resident frames must be in range; frame is ignored for nonresident entries. Aliased physical frames are permitted. Requests have address and access (read/write). Fault priority: address outside [0,page_size*virtual_pages), missing/nonresident page, write to read-only page. Otherwise physical=frame*page_size+address%page_size. statuses and physical are aligned with requests; physical=-1 for faults. No TLB, page replacement or state changes.

The input/output field shapes and Enum values are declared in contract.py. Invalid semantic inputs raise ValueError (except malformed packet contents, which the inspection task reports explicitly). No model is used to judge results. The verifier independently recomputes the expected answer, compares every result field, and reads the actual result.json. A matching declaration alone is insufficient. Acceptance is binary; the framework score is 1 for valid and 0 for invalid.

### Example task input

```json
{
  "page_size": 16,
  "virtual_pages": 4,
  "frames": 2,
  "entries": [
    {
      "page": 0,
      "resident": true,
      "frame": 1,
      "writable": false
    },
    {
      "page": 1,
      "resident": false,
      "frame": 99,
      "writable": true
    },
    {
      "page": 2,
      "resident": true,
      "frame": 1,
      "writable": true
    }
  ],
  "requests": [
    {
      "address": 0,
      "access": "read"
    },
    {
      "address": 15,
      "access": "write"
    },
    {
      "address": 16,
      "access": "read"
    },
    {
      "address": 32,
      "access": "write"
    },
    {
      "address": 63,
      "access": "read"
    },
    {
      "address": 64,
      "access": "read"
    },
    {
      "address": -1,
      "access": "write"
    }
  ]
}
```

In RUSH Lab, request the `page-translate` task with this structured input. The agent calls `translate_addresses`, passes its complete output to save_result, and submits the saved output. A model and RUSH Lab access are needed for this step; pytest does not establish agent success.

## Layout

- contract.py: typed tools, task and outputs.
- src/plugin/: MCP server, computation and file saving.
- verifier/: independent deterministic oracle and artifact checks.
- tests/: public pedagogical task inputs and regression checks, not experiment logs.
- ui/ and product/: schema-based result display and marketplace metadata.

## Develop and run

Requires Git, uv and Python 3.12+. From this repository:

```sh
uv sync --frozen --extra dev --no-editable
uv run --frozen --no-editable pytest -q
uv run --frozen --no-editable ruff check .
uv lock --check
```

Normal (non-editable) installation is intentional: it also checks packaged source imports. After editing source, rerun uv sync with --reinstall-package nanoagent-kw118-page-translate. Do not copy another project's virtual environment.

The manifest's runtime remains the official `[uv, run, --frozen, python, -m, plugin]`. The host supplies NANOAGENT_WORKSPACE. No API keys or plugin network hosts are needed. All writes stay in the workspace. Existing symlink destinations are rejected. Runtime files, logs and the milestone report belong outside this repository.

### Validation and limitations

Tests cover the domain boundaries, wrong results, missing/malformed artifacts, schema failures and symlink protection. Fixtures are intentionally small public teaching inputs representing the actual task contract, not hardware performance samples. Tools and oracle use separate implementations. Local correctness does not establish marketplace installation or model behavior; those require recorded real platform runs.
