"""Print which package Python resolves for `app`.

Run from the project root:
    python scripts/check_import_origin.py
"""
import importlib.util
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECTED_APP = os.path.join(ROOT, "app", "__init__.py")


def resolve_app_origin() -> str | None:
    spec = importlib.util.find_spec("app")
    return os.path.abspath(spec.origin) if spec and spec.origin else None


def main() -> int:
    raw_origin = resolve_app_origin()
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    rooted_origin = resolve_app_origin()

    print(f"cwd: {os.getcwd()}")
    print(f"expected app: {EXPECTED_APP}")
    print(f"resolved app before adding project root: {raw_origin}")
    print(f"resolved app with project root first: {rooted_origin}")
    print("python path:")
    for path in sys.path:
        print(f"  {path}")

    if rooted_origin != EXPECTED_APP:
        print("\nImport conflict: Python is not using MovieRecommender/app.")
        return 1

    print("\nOK: Python is using MovieRecommender/app.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
