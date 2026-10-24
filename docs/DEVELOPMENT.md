# Development

Requires Python 3.10 or newer. The runtime uses only the Python standard library.

## Run locally

```sh
python -m pip install -e .
robloxlx doctor
robloxlx compatibility
robloxlx self-test
```

From a source checkout, tests can also be run without installing the package:

```sh
PYTHONPATH=src python -m unittest discover -s tests/unit -v
PYTHONPATH=src python -m robloxlx.cli version
python -m compileall -q src tests
```

Keep diagnostics read-only, use fixed subprocess arguments and timeouts, and test without Roblox credentials or production game sessions. Do not add client patching, code injection, anti-cheat evasion, secret capture, or protocol manipulation. Use Conventional Commit subjects such as `feat:`, `fix:`, `docs:`, `test:`, and `chore:`.
