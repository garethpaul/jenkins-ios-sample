import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_TESTS = ROOT / "scripts" / "run-tests.sh"


class CIBoundaryTests(unittest.TestCase):
    def test_xcodebuild_receives_no_retired_provider_credentials(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            capture_path = temporary_path / "capture.txt"
            fake_xcodebuild = temporary_path / "xcodebuild"
            fake_upload = temporary_path / "fake-upload"
            fake_upload.write_text("#!/bin/sh\ntouch \"$FAKE_UPLOAD_MARKER\"\n", encoding="utf-8")
            fake_upload.chmod(0o755)
            fake_xcodebuild.write_text(
                "#!/bin/sh\n"
                "{\n"
                "  printf 'FABRIC=%s\\n' \"${FABRIC_API_KEY-unset}\"\n"
                "  printf 'SECRET=%s\\n' \"${CRASHLYTICS_BUILD_SECRET-unset}\"\n"
                "  printf 'ARGS='\n"
                "  printf '%s|' \"$@\"\n"
                "  printf '\\n'\n"
                "} > \"$CAPTURE_PATH\"\n",
                encoding="utf-8",
            )
            fake_xcodebuild.chmod(0o755)
            marker_path = temporary_path / "upload-ran"
            environment = os.environ.copy()
            environment.update(
                {
                    "PATH": f"{temporary_path}:{environment['PATH']}",
                    "CAPTURE_PATH": str(capture_path),
                    "FABRIC_API_KEY": "a" * 40,
                    "CRASHLYTICS_BUILD_SECRET": "b" * 64,
                    "FABRIC_UPLOAD_TOOL": str(fake_upload),
                    "FAKE_UPLOAD_MARKER": str(marker_path),
                    "IOS_DESTINATION": "platform=iOS Simulator,id=TEST-DEVICE",
                }
            )

            subprocess.run([str(RUN_TESTS)], cwd=ROOT, env=environment, check=True)

            capture = capture_path.read_text(encoding="utf-8")
            self.assertIn("FABRIC=unset", capture)
            self.assertIn("SECRET=unset", capture)
            self.assertNotIn("a" * 40, capture)
            self.assertNotIn("b" * 64, capture)
            self.assertIn("CODE_SIGNING_ALLOWED=NO", capture)
            self.assertIn("CODE_SIGNING_REQUIRED=NO", capture)
            self.assertIn("test|", capture)
            self.assertNotIn("archive|", capture)
            self.assertFalse(marker_path.exists())

    def test_project_override_rejects_symlink(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary_directory:
            temporary_path = Path(temporary_directory)
            symlink_path = temporary_path / "Project.xcodeproj"
            symlink_path.symlink_to(ROOT / "Jenkins iOS Sample.xcodeproj", target_is_directory=True)
            fake_xcodebuild = temporary_path / "xcodebuild"
            fake_xcodebuild.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            fake_xcodebuild.chmod(0o755)
            environment = os.environ.copy()
            environment.update(
                {
                    "PATH": f"{temporary_path}:{environment['PATH']}",
                    "XCODE_PROJECT": str(symlink_path.relative_to(ROOT)),
                    "IOS_DESTINATION": "platform=iOS Simulator,id=TEST-DEVICE",
                }
            )
            completed = subprocess.run(
                [str(RUN_TESTS)],
                cwd=ROOT,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("regular repository project directory", completed.stderr)

    def test_project_override_rejects_symlinked_parent(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary_directory:
            temporary_path = Path(temporary_directory)
            parent_link = temporary_path / "linked-parent"
            parent_link.symlink_to(ROOT, target_is_directory=True)
            fake_xcodebuild = temporary_path / "xcodebuild"
            fake_xcodebuild.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            fake_xcodebuild.chmod(0o755)
            environment = os.environ.copy()
            environment.update(
                {
                    "PATH": f"{temporary_path}:{environment['PATH']}",
                    "XCODE_PROJECT": str((parent_link / "Jenkins iOS Sample.xcodeproj").relative_to(ROOT)),
                    "IOS_DESTINATION": "platform=iOS Simulator,id=TEST-DEVICE",
                }
            )
            completed = subprocess.run(
                [str(RUN_TESTS)],
                cwd=ROOT,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("regular repository project directory", completed.stderr)

    def test_hanging_xcodebuild_is_terminated_at_deadline(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            fake_xcodebuild = temporary_path / "xcodebuild"
            fake_xcodebuild.write_text("#!/bin/sh\nsleep 30\n", encoding="utf-8")
            fake_xcodebuild.chmod(0o755)
            environment = os.environ.copy()
            environment.update(
                {
                    "PATH": f"{temporary_path}:{environment['PATH']}",
                    "IOS_DESTINATION": "platform=iOS Simulator,id=TEST-DEVICE",
                    "XCODEBUILD_TIMEOUT_SECONDS": "1",
                }
            )
            started = time.monotonic()
            completed = subprocess.run(
                [str(RUN_TESTS)],
                cwd=ROOT,
                env=environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5,
            )

            self.assertEqual(completed.returncode, 124)
            self.assertLess(time.monotonic() - started, 4)
            self.assertIn("timed out after 1 seconds", completed.stderr)


if __name__ == "__main__":
    unittest.main()
