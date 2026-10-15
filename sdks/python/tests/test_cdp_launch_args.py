"""Tests for _cdp_launch_args — no real browser is started.

We stub the two external runtime dependencies (patchright and httpx)
before touching the shardx package so the modules load cleanly.
"""
import sys
import os
import types
import unittest

# ---------------------------------------------------------------------------
# Lightweight stubs for optional runtime-only dependencies so we can import
# shardx.browser without installing patchright or httpx.
# ---------------------------------------------------------------------------

def _make_stub(*names: str) -> None:
    for name in names:
        if name not in sys.modules:
            stub = types.ModuleType(name)
            # Give it a few attribute placeholders referenced at import time.
            stub.__all__ = []  # type: ignore[attr-defined]
            sys.modules[name] = stub

_make_stub("patchright", "patchright.async_api", "httpx", "httpx._models")

# Provide the specific names __init__.py and other modules pull from patchright.
_pr_async = sys.modules["patchright.async_api"]
_pr_async.Browser = type("Browser", (), {})  # type: ignore[attr-defined]
_pr_async.async_playwright = lambda: None    # type: ignore[attr-defined]
sys.modules["patchright"].async_api = _pr_async  # type: ignore[attr-defined]

# httpx.Client and related
_httpx = sys.modules["httpx"]
_httpx.Client = type("Client", (), {"__init__": lambda self, **kw: None})  # type: ignore
_httpx.Limits = type("Limits", (), {"__init__": lambda self, **kw: None})  # type: ignore
_httpx.Timeout = type("Timeout", (), {"__init__": lambda self, *a, **kw: None})  # type: ignore
_httpx.HTTPError = Exception  # type: ignore
_httpx.RequestError = Exception  # type: ignore

# Ensure the shardx package directory is on sys.path.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Now we can safely import from the package.
from shardx.browser import _cdp_launch_args  # noqa: E402  (after stub setup)

# ---------------------------------------------------------------------------
AUTOMATION_FLAG = "--shardx-automation"
REMOTE_DEBUG    = "--remote-debugging-port=0"
ALLOW_ORIGINS   = "--remote-allow-origins=*"


class TestCdpLaunchArgs(unittest.TestCase):
    def test_cdp_enabled_includes_automation_flag(self):
        args = _cdp_launch_args(True)
        self.assertIn(AUTOMATION_FLAG, args)

    def test_cdp_enabled_includes_remote_debugging(self):
        args = _cdp_launch_args(True)
        self.assertIn(REMOTE_DEBUG, args)
        self.assertIn(ALLOW_ORIGINS, args)

    def test_cdp_enabled_automation_flag_is_last(self):
        """Automation flag should immediately follow remote-debugging args."""
        args = _cdp_launch_args(True)
        self.assertEqual(args[-1], AUTOMATION_FLAG)

    def test_no_cdp_returns_empty(self):
        args = _cdp_launch_args(False)
        self.assertEqual(args, [])

    def test_no_cdp_no_automation_flag(self):
        args = _cdp_launch_args(False)
        self.assertNotIn(AUTOMATION_FLAG, args)

    def test_no_cdp_no_remote_debugging(self):
        args = _cdp_launch_args(False)
        self.assertNotIn(REMOTE_DEBUG, args)


if __name__ == "__main__":
    unittest.main()
