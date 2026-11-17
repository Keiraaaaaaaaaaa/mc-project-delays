"""A tiny test runner, so the tests also work without pytest:

    python tests/test_core.py
    python tests/test_part4.py
    python tests/test_part5.py
"""

import sys


def run(namespace):
    tests = [(name, f) for name, f in sorted(namespace.items())
             if name.startswith("test_") and callable(f)]
    failed, todo = 0, 0
    for name, test in tests:
        try:
            test()
            print(f"ok    {name}")
        except NotImplementedError as exc:
            todo += 1
            print(f"TODO  {name}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {name}: {exc!r}")
    summary = f"\n{len(tests) - failed - todo}/{len(tests)} passed"
    if todo:
        summary += f", {todo} not implemented yet"
    print(summary)
    sys.exit(1 if failed or todo else 0)
