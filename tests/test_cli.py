"""Smoke tests proving the installed CLI entry points work end to end."""
import contextlib
import io
import json
import unittest

from legends_ultimate_captions.cli import load_config, main


class CliSmokeTests(unittest.TestCase):
    def run_main(self, argv):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(argv)
        return code, stdout.getvalue()

    def test_doctor_reports_json(self) -> None:
        code, out = self.run_main(["doctor"])
        self.assertEqual(code, 0)
        report = json.loads(out)
        self.assertEqual(report["project"], "Legends Ultimate Captions")
        self.assertIn("config_profile", report)

    def test_policy_report_lists_rules(self) -> None:
        code, out = self.run_main(["policy-report"])
        self.assertEqual(code, 0)
        rules = json.loads(out)
        self.assertGreater(len(rules), 0)
        self.assertIn("match", rules[0])

    def test_normalize_applies_policy(self) -> None:
        code, out = self.run_main(["normalize", "low", "raw."])
        self.assertEqual(code, 0)
        self.assertIn("LoRA", out)

    def test_normalize_manifest_shape(self) -> None:
        code, out = self.run_main(["normalize", "--manifest", "hello", "world"])
        self.assertEqual(code, 0)
        manifest = json.loads(out)
        self.assertEqual(manifest["normalized_text"], "hello world")

    def test_default_config_loads(self) -> None:
        config = load_config()
        self.assertIn("profile", config)


if __name__ == "__main__":
    unittest.main()
