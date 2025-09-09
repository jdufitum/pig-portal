"""
Compatibility shim for an accidental package/module name collision.

This package directory (app/db) shadows the sibling module file (app/db.py).
Many modules import from `app.db` expecting the module file that defines
`engine` and `SessionLocal`. To preserve that behavior, we dynamically load the
module from its file path and re-export the expected symbols here.
"""

from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

_this_dir = Path(__file__).resolve().parent
_module_path = _this_dir.parent / "db.py"

_spec = spec_from_file_location("app._db_module", str(_module_path))
if _spec is None or _spec.loader is None:
    raise ImportError(f"Cannot load app.db module from {_module_path}")
_mod = module_from_spec(_spec)
_spec.loader.exec_module(_mod)  # type: ignore[assignment]

engine = _mod.engine
SessionLocal = _mod.SessionLocal

__all__ = ["SessionLocal", "engine"]