import os
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.repository_policy import inspect_repository


class RepositoryPolicyTests(unittest.TestCase):
    def write(self, root, path, content):
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def write_executable(self, root, path, content):
        self.write(root, path, content)
        (root / path).chmod(0o755)

    def write_minimal_make_checkout(self, root, makefile, baseline_label="real"):
        self.write(root, "Makefile", makefile)
        self.write(
            root,
            "scripts/check-baseline.py",
            'print("{} baseline")\n'.format(baseline_label),
        )
        self.write_executable(
            root,
            "scripts/run-tests.sh",
            '#!/bin/sh\necho "{} run-tests"\n'.format(baseline_label),
        )
        self.write(
            root,
            "tests/test_{}.py".format(baseline_label),
            "import unittest\n\n"
            "class Smoke(unittest.TestCase):\n"
            "    def test_{}(self):\n"
            "        self.assertTrue(True)\n".format(baseline_label),
        )

    def write_fake_xcodebuild(self, root):
        self.write_executable(root, "bin/xcodebuild", "#!/bin/sh\nexit 0\n")
        environment = os.environ.copy()
        environment["PATH"] = "{}{}{}".format(root / "bin", os.pathsep, environment["PATH"])
        return environment

    def test_rejects_retired_provider_execution_surfaces(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self.write(root, "Jenkins iOS Sample/AppDelegate.swift", "import Fabric\nFabric.with([])\n")
            self.write(root, "Jenkins iOS Sample.xcodeproj/project.pbxproj", "./Fabric.framework/run KEY SECRET\n")
            self.write(root, "Jenkins iOS Sample/Info.plist", "<key>Fabric</key>\n")
            self.write(root, "Fabric.framework/run", "binary")

            failures = inspect_repository(root)

            self.assertTrue(any("retired Fabric import" in failure for failure in failures))
            self.assertTrue(any("retired Fabric upload" in failure for failure in failures))
            self.assertTrue(any("retired Fabric plist" in failure for failure in failures))
            self.assertTrue(any("vendored retired-provider artifact" in failure for failure in failures))

    def test_rejects_symlinks_and_unsafe_workflow_permissions(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self.write(
                root,
                ".github/workflows/check.yml",
                "permissions: write-all\nsteps:\n  - run: echo ${{ secrets.FABRIC_API_KEY }}\n",
            )
            (root / "linked-project").symlink_to(root / ".github")

            failures = inspect_repository(root)

            self.assertTrue(any("symlink" in failure for failure in failures))
            self.assertTrue(any("read-only workflow permissions" in failure for failure in failures))
            self.assertTrue(any("workflow secret reference" in failure for failure in failures))

    def test_rejects_each_ci_boundary_mutation(self):
        mutations = {
            "persisted checkout credentials": (
                ".github/workflows/check.yml",
                "permissions:\n  contents: read\nsteps:\n  - uses: actions/checkout@deadbeef\n    with:\n      persist-credentials: true\n",
                "disable persisted credentials",
            ),
            "artifact archive": (
                ".github/workflows/check.yml",
                "permissions:\n  contents: read\nsteps:\n  - run: xcodebuild archive\n  - uses: actions/checkout@deadbeef\n    with:\n      persist-credentials: false\n",
                "must not sign, archive, or upload",
            ),
            "shell build phase": (
                "Jenkins iOS Sample.xcodeproj/project.pbxproj",
                "PBXShellScriptBuildPhase\nshellScript = upload;\n",
                "must not execute shell upload phases",
            ),
            "signing identity": (
                "Jenkins iOS Sample.xcodeproj/project.pbxproj",
                'CODE_SIGN_IDENTITY = "iPhone Developer";\n',
                "must not pin a signing identity",
            ),
            "missing credential stripping": (
                "scripts/run-tests.sh",
                "xcodebuild CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO CODE_SIGN_IDENTITY= test\n",
                "unset FABRIC_API_KEY",
            ),
        }
        for name, (path, content, expected) in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary_directory:
                root = Path(temporary_directory)
                self.write(root, "Makefile", "ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))\n")
                self.write(root, path, content)
                failures = inspect_repository(root)
                self.assertTrue(any(expected in failure for failure in failures), failures)

    def test_makefile_resolves_spaced_checkout_from_external_directory(self):
        repository_root = Path(__file__).resolve().parents[1]
        makefile = (repository_root / "Makefile").read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            checkout = temporary_root / "checkout with spaces 'quoted' [hostile]"
            external = temporary_root / "external caller"
            checkout.mkdir()
            external.mkdir()
            (checkout / "Makefile").write_text(makefile, encoding="utf-8")

            for target in ("check", "lint", "test", "build"):
                for extra_arguments in ((), ("ROOT=/tmp/untrusted",), ("-e", "ROOT=/tmp/untrusted")):
                    with self.subTest(target=target, extra_arguments=extra_arguments):
                        result = subprocess.run(
                            ["make", "--dry-run", "-f", str(checkout / "Makefile"),
                             *extra_arguments, target],
                            cwd=external,
                            check=True,
                            capture_output=True,
                            text=True,
                        )

                        self.assertIn("scripts/check-baseline.py", result.stdout)
                        self.assertIn("cd {}".format(shlex.quote(str(checkout))), result.stdout)
                        self.assertNotIn("/tmp/untrusted", result.stdout)

    def test_make_test_ignores_later_committed_root_override(self):
        repository_root = Path(__file__).resolve().parents[1]
        makefile = (
            (repository_root / "Makefile").read_text(encoding="utf-8")
            + "\noverride ROOT := $(CURDIR)/fake-root\n"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            checkout = temporary_root / "checkout with spaces 'quoted' [hostile]"
            checkout.mkdir()
            self.write_minimal_make_checkout(checkout, makefile)
            self.write_minimal_make_checkout(checkout / "fake-root", "", "fake")
            environment = self.write_fake_xcodebuild(temporary_root)

            result = subprocess.run(
                ["make", "test"],
                cwd=checkout,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("real baseline", result.stdout)
            self.assertIn("real run-tests", result.stdout)
            self.assertNotIn("fake baseline", result.stdout)
            self.assertNotIn("fake run-tests", result.stdout)

    def test_repository_policy_rejects_later_root_override(self):
        repository_root = Path(__file__).resolve().parents[1]
        makefile = (repository_root / "Makefile").read_text(encoding="utf-8")

        for override_line in (
            "override ROOT := /tmp/untrusted",
            "check: override ROOT := /tmp/untrusted",
        ):
            with self.subTest(override_line=override_line), tempfile.TemporaryDirectory() as temporary_directory:
                root = Path(temporary_directory)
                self.write(root, "Makefile", "{}\n{}\n".format(makefile, override_line))

                failures = inspect_repository(root)

                self.assertTrue(
                    any("repository root independently" in failure for failure in failures),
                    failures,
                )

    def test_makefile_executes_from_double_quote_checkout_path(self):
        repository_root = Path(__file__).resolve().parents[1]
        makefile = (repository_root / "Makefile").read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            checkout = temporary_root / "checkout with spaces 'quoted' [hostile] \"double"
            external = temporary_root / "external caller"
            checkout.mkdir()
            external.mkdir()
            self.write_minimal_make_checkout(checkout, makefile)

            result = subprocess.run(
                ["make", "-f", str(checkout / "Makefile"), "check"],
                cwd=external,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("real baseline", result.stdout)

    def test_makefile_uses_current_file_when_earlier_makefile_is_loaded(self):
        repository_root = Path(__file__).resolve().parents[1]
        makefile = (repository_root / "Makefile").read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            checkout = temporary_root / "checkout with spaces [hostile]"
            external = temporary_root / "external caller"
            early = temporary_root / "early.mk"
            checkout.mkdir()
            external.mkdir()
            early.write_text("# earlier makefile\n", encoding="utf-8")
            self.write_minimal_make_checkout(checkout, makefile)

            result = subprocess.run(
                ["make", "--dry-run", "-f", str(early), "-f", str(checkout / "Makefile"), "check"],
                cwd=external,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn(shlex.quote(str(checkout)), result.stdout)
            self.assertNotIn(str(early), result.stdout)

    def test_makefile_rejects_makefile_list_injection(self):
        repository_root = Path(__file__).resolve().parents[1]
        makefile = (repository_root / "Makefile").read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            checkout = temporary_root / "checkout with spaces 'quoted' [hostile]"
            external = temporary_root / "external caller"
            checkout.mkdir()
            external.mkdir()
            (checkout / "Makefile").write_text(makefile, encoding="utf-8")

            environment = os.environ.copy()
            environment["MAKEFILE_LIST"] = "/tmp/untrusted"
            attacks = (
                (["make", "--dry-run", "-f", str(checkout / "Makefile"),
                  "MAKEFILE_LIST=/tmp/untrusted", "check"], None),
                (["make", "-e", "--dry-run", "-f", str(checkout / "Makefile"), "check"],
                 environment),
            )

            for command, attack_environment in attacks:
                with self.subTest(command=command):
                    result = subprocess.run(
                        command,
                        cwd=external,
                        env=attack_environment,
                        check=False,
                        capture_output=True,
                        text=True,
                    )

                    self.assertNotEqual(0, result.returncode, result.stdout)
                    self.assertIn("MAKEFILE_LIST must not be overridden", result.stderr)

    def test_repository_policy_requires_makefile_list_origin_guard(self):
        repository_root = Path(__file__).resolve().parents[1]
        makefile = (repository_root / "Makefile").read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            self.write(
                root,
                "Makefile",
                makefile.replace(
                    "ifneq ($(origin MAKEFILE_LIST),file)\n"
                    "$(error MAKEFILE_LIST must not be overridden)\n"
                    "endif\n",
                    "",
                    1,
                ),
            )

            failures = inspect_repository(root)

            self.assertTrue(
                any("reject MAKEFILE_LIST overrides" in failure for failure in failures),
                failures,
            )


if __name__ == "__main__":
    unittest.main()
