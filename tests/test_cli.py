"""Smoke tests proving the installed CLI entry points work end to end."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from legends_captions.cli import load_config, main


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
        self.assertEqual(report["project"], "Legends Captions")
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

    def test_render_ass_inline_text(self) -> None:
        code, out = self.run_main(["render-ass", "--uppercase", "low", "raw", "teaches"])
        self.assertEqual(code, 0)
        self.assertIn("[Script Info]", out)
        self.assertIn("Dialogue: 0,", out)
        self.assertIn("LORA", out)

    def test_render_ass_json_input_and_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            input_path = tmp_dir / "words.json"
            ass_path = tmp_dir / "captions.ass"
            manifest_path = tmp_dir / "manifest.json"
            input_path.write_text(
                json.dumps(
                    {
                        "words": [
                            {"text": "low", "start": 0.0, "end": 0.3},
                            {"text": "raw", "start": 0.3, "end": 0.6},
                            {"text": "teaches", "start": 0.6, "end": 1.0},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            code, out = self.run_main(
                [
                    "render-ass",
                    "--input",
                    str(input_path),
                    "--output",
                    str(ass_path),
                    "--manifest-output",
                    str(manifest_path),
                    "--uppercase",
                ]
            )
            self.assertEqual(code, 0)
            receipt = json.loads(out)
            self.assertEqual(receipt["status"], "ok")
            self.assertEqual(receipt["caption_text"], "LORA TEACHES")
            self.assertTrue(ass_path.is_file())
            self.assertTrue(manifest_path.is_file())
            self.assertIn("Dialogue: 0,0:00:00.00,0:00:00.60,LegendsActive,,0,0,0,,LORA", ass_path.read_text(encoding="utf-8"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["normalized_text"], "LoRA teaches")

    def test_default_config_loads(self) -> None:
        config = load_config()
        self.assertIn("profile", config)


if __name__ == "__main__":
    unittest.main()
