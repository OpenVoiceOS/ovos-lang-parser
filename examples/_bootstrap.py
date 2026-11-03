"""Shared setup for the example scripts.

Importing this module does two convenience things so the examples run cleanly
from a checkout:

* Puts the repository root on ``sys.path`` so ``import ovos_lang_parser`` uses
  the code in this checkout, even if an older release is also installed.
* Quiets the OVOS logger so example output is not buried in deprecation notices.

None of this is needed in your own project — there you just
``pip install ovos-lang-parser`` and ``import ovos_lang_parser``.
"""
import logging
import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

logging.getLogger("OVOS").setLevel(logging.ERROR)
