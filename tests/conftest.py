import sys
import pathlib

# Ensure project root is on sys.path so 'app' package imports work during tests.
# This makes pytest/uv-run pytest find the local package regardless of CWD.
ROOT = pathlib.Path(__file__).resolve().parents[1]
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

