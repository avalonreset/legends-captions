"""Smoke and security regression tests proving the installed CLI entry points work end to end."""
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from legends_captions.ass_builder import (
    AssEvent,
    AssStyle,
    ass_time,
    build_ass_document,
    escape_ass,
    escape_ffmpeg_ass_filter,
    format_ffmpeg_ass_filtergraph,
)
from legends_captions.cli import load_config, main, resolve_project_root


class CliSmokeTests(unittest.TestCase):
    def run_main(self, argv):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_doctor_reports_json(self) -> None:
        code, out, _ = self.run_main(["doctor"])
        self.assertEqual(code, 0)
        report = json.loads(out)
        self.assertEqual(report["project"], "Legends Captions")
        self.assertIn("config_profile", report)
        self.assertIn("source_checkout", report)

    def test_wheel_install_project_root_does_not_resolve_into_venv_lib(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fake_root = Path(tmp) / "venv" / "Lib"
            fake_root.mkdir(parents=True)
            with mock.patch("legends_captions.cli._CANDIDATE_REPO_ROOT", fake_root):
                resolved = resolve_project_root()
                self.assertEqual(resolved, Path.cwd().resolve())

    def test_policy_report_lists_rules(self) -> None:
        code, out, _ = self.run_main(["policy-report"])
        self.assertEqual(code, 0)
        rules = json.loads(out)
        self.assertGreater(len(rules), 0)
        self.assertIn("match", rules[0])

    def test_normalize_applies_policy(self) -> None:
        code, out, _ = self.run_main(["normalize", "low", "raw."])
        self.assertEqual(code, 0)
        self.assertIn("LoRA", out)

    def test_normalize_manifest_shape(self) -> None:
        code, out, _ = self.run_main(["normalize", "--manifest", "hello", "world"])
        self.assertEqual(code, 0)
        manifest = json.loads(out)
        self.assertEqual(manifest["normalized_text"], "hello world")

    def test_render_ass_inline_text(self) -> None:
        code, out, _ = self.run_main(["render-ass", "--uppercase", "low", "raw", "teaches"])
        self.assertEqual(code, 0)
        self.assertIn("[Script Info]", out)
        self.assertIn("Dialogue: 0,", out)
        self.assertIn("LORA", out)

    def test_render_ass_json_input_and_outputs_and_overwrite_guard(self) -> None:
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
            code, out, _ = self.run_main(
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
            self.assertIn(
                "Dialogue: 0,0:00:00.00,0:00:00.60,LegendsActive,,0,0,0,,LORA",
                ass_path.read_text(encoding="utf-8"),
            )
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["normalized_text"], "LoRA teaches")

            # Fail closed on second write without --overwrite
            code2, _, err2 = self.run_main(
                [
                    "render-ass",
                    "--input",
                    str(input_path),
                    "--output",
                    str(ass_path),
                    "--uppercase",
                ]
            )
            self.assertEqual(code2, 2)
            self.assertIn("--overwrite", err2)

            # Succeed when --overwrite is supplied
            code3, _, _ = self.run_main(
                [
                    "render-ass",
                    "--input",
                    str(input_path),
                    "--output",
                    str(ass_path),
                    "--manifest-output",
                    str(manifest_path),
                    "--overwrite",
                    "--uppercase",
                ]
            )
            self.assertEqual(code3, 0)

    def test_ffmpeg_filter_escapes_windows_colons_and_rejects_injection(self) -> None:
        self.assertEqual(len(escape_ffmpeg_ass_filter("'")), 6)
        escaped = escape_ffmpeg_ass_filter(r"C:\work\clip[1],test's;final.ass")
        self.assertEqual(escaped, r"C\:\\work\\clip\[1\]\,test'" + "\\" * 3 + r"''s\;final.ass")
        fg = format_ffmpeg_ass_filtergraph(r"C:\work\captions.ass")
        self.assertEqual(fg, r"[0:v]setpts=PTS-STARTPTS,ass=filename='C\:\\work\\captions.ass'[v]")
        fg_quote = format_ffmpeg_ass_filtergraph(r"C:\work\O'Neil_captions.ass")
        self.assertEqual(
            fg_quote,
            r"[0:v]setpts=PTS-STARTPTS,ass=filename='C\:\\work\\O'" + "\\" * 3 + r"''Neil_captions.ass'[v]",
        )

        code, out, _ = self.run_main(["ffmpeg-filter", "--ass", r"C:\work\captions.ass", "--json"])
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["escaped_filename"], r"C\:\\work\\captions.ass")

        with self.assertRaises(ValueError):
            escape_ffmpeg_ass_filter("bad\ninjection.ass")
        with self.assertRaises(ValueError):
            escape_ffmpeg_ass_filter("-option.ass")

    def test_ass_builder_sanitizes_carriage_returns_styles_and_nonfinite_times(self) -> None:
        self.assertEqual(escape_ass("line1\r\nline2\r{tag}"), r"line1\Nline2\N\{tag\}")
        with self.assertRaises(ValueError):
            AssStyle(font="Montserrat,0,0\nDialogue: 0,0:00:00.00")
        with self.assertRaises(ValueError):
            AssStyle(font_size=0)
        with self.assertRaises(ValueError):
            ass_time(float("nan"))
        with self.assertRaises(ValueError):
            ass_time(float("inf"))
        with self.assertRaises(ValueError):
            build_ass_document([AssEvent(start=0.0, end=1.0, text="ok")], width=0, height=3840)

    def test_cli_rejects_nonfinite_json_and_invalid_font(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad_json = Path(tmp) / "nan.json"
            bad_json.write_text('{"words": [{"text": "hi", "start": NaN, "end": 1.0}]}', encoding="utf-8")
            code, _, err = self.run_main(["render-ass", "--input", str(bad_json)])
            self.assertEqual(code, 2)
            self.assertIn("Non-finite", err)

        code2, _, err2 = self.run_main(["render-ass", "--font", "Bad,Font", "hello"])
        self.assertEqual(code2, 2)
        self.assertIn("Invalid", err2)

    def test_cli_refuses_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            target = tmp_dir / "real.json"
            target.write_text('{"words": [{"text": "hi", "start": 0.0, "end": 0.5}]}', encoding="utf-8")
            with mock.patch.object(Path, "is_symlink", return_value=True):
                code, _, err = self.run_main(["render-ass", "--input", str(target)])
            self.assertEqual(code, 2)
            self.assertIn("symlink", err.lower())

    def test_default_config_loads(self) -> None:
        config = load_config()
        self.assertIn("profile", config)


if __name__ == "__main__":
    unittest.main()
