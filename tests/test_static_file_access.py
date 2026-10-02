"""Regression tests: the proof API must never serve files from its working directory."""

import sys
import types
import unittest
from unittest.mock import Mock

# Importing the server module must not start a server or require optional runtime
# configuration dependencies merely to test its request handler.
dotenv_stub = types.ModuleType("dotenv")
dotenv_stub.load_dotenv = lambda **_kwargs: None
sys.modules.setdefault("dotenv", dotenv_stub)

from https_server import SimpleHTTPSRequestHandler


class StaticFileAccessTests(unittest.TestCase):
    def assert_method_denied(self, method_name):
        handler = SimpleHTTPSRequestHandler.__new__(SimpleHTTPSRequestHandler)
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()

        getattr(handler, method_name)()

        handler.send_response.assert_called_once_with(405)
        handler.send_header.assert_any_call("Allow", "POST, OPTIONS")
        handler.send_header.assert_any_call("Content-Length", "0")
        handler.end_headers.assert_called_once_with()

    def test_get_does_not_serve_working_directory_files(self):
        self.assert_method_denied("do_GET")

    def test_head_does_not_serve_working_directory_metadata(self):
        self.assert_method_denied("do_HEAD")


if __name__ == "__main__":
    unittest.main()
