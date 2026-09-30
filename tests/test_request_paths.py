import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from request_paths import build_job_paths, validate_request_id


class RequestPathTests(unittest.TestCase):
    def test_accepts_safe_request_id(self):
        with TemporaryDirectory() as directory:
            input_path, output_path = build_job_paths("job_2026-09-30", Path(directory))

        self.assertEqual(input_path.name, "job_2026-09-30.json")
        self.assertEqual(output_path.name, "job_2026-09-30")

    def test_rejects_path_traversal(self):
        for request_id in ("../outside", "nested/job", "", "job name", "/tmp/job"):
            with self.assertRaises(ValueError):
                validate_request_id(request_id)


if __name__ == "__main__":
    unittest.main()
