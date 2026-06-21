import os
import re
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

    def hosted_validation_command(self, repository_root):
        workflow = (repository_root / ".github/workflows/check.yml").read_text(encoding="utf-8")
        match = re.search(
            r"(?m)^      - name: Validate baseline and XCTest\n"
            r"        run: (?:(?!\|)([^\n]+)|\|\n((?:          [^\n]*(?:\n|$))+))",
            workflow,
        )
        self.assertIsNotNone(match, workflow)
        if match.group(1):
            return match.group(1)
        return "\n".join(line[10:] for line in match.group(2).splitlines())

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
        repository_root = Path(__file__).resolve().parents[1]
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
            "mutable Make hosted entrypoint": (
                ".github/workflows/check.yml",
                "permissions:\n  contents: read\nsteps:\n"
                "  - uses: actions/checkout@deadbeef\n"
                "    with:\n      persist-credentials: false\n"
                "  - name: Validate baseline and XCTest\n"
                "    run: make test\n",
                "exact reviewed workflow",
            ),
            "job PATH environment": (
                ".github/workflows/check.yml",
                (repository_root / ".github/workflows/check.yml").read_text(encoding="utf-8").replace(
                    "    runs-on: macos-15\n",
                    "    runs-on: macos-15\n    env:\n      PATH: .:${{ env.PATH }}\n",
                ),
                "exact reviewed workflow",
            ),
            "step environment": (
                ".github/workflows/check.yml",
                (repository_root / ".github/workflows/check.yml").read_text(encoding="utf-8").replace(
                    "      - name: Validate baseline and XCTest\n",
                    "      - name: Validate baseline and XCTest\n        env:\n          PATH: .:${{ env.PATH }}\n",
                ),
                "exact reviewed workflow",
            ),
            "custom validation shell": (
                ".github/workflows/check.yml",
                (repository_root / ".github/workflows/check.yml").read_text(encoding="utf-8").replace(
                    "        run: |\n",
                    "        shell: python\n        run: |\n",
                ),
                "exact reviewed workflow",
            ),
            "extra workflow step": (
                ".github/workflows/check.yml",
                (repository_root / ".github/workflows/check.yml").read_text(encoding="utf-8")
                + "      - run: echo extra\n",
                "exact reviewed workflow",
            ),
            "validation command addition": (
                ".github/workflows/check.yml",
                (repository_root / ".github/workflows/check.yml").read_text(encoding="utf-8").replace(
                    "          /bin/sh ./scripts/run-tests.sh\n",
                    "          echo injected\n          /bin/sh ./scripts/run-tests.sh\n",
                ),
                "exact reviewed workflow",
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

    def test_make_test_reaches_real_policy_before_later_root_overrides(self):
        repository_root = Path(__file__).resolve().parents[1]
        makefile = (repository_root / "Makefile").read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_root = Path(temporary_directory)
            environment = self.write_fake_xcodebuild(temporary_root)

            for label, override_line in (
                ("global", "override ROOT := $(CURDIR)/fake-root"),
                ("all-targets", "check lint test build: override ROOT := $(CURDIR)/fake-root"),
                ("check-target", "check: override ROOT := $(CURDIR)/fake-root"),
            ):
                with self.subTest(override_line=override_line):
                    hostile_checkout = temporary_root / label
                    hostile_checkout.mkdir()
                    self.write_minimal_make_checkout(
                        hostile_checkout,
                        "{}\n{}\n".format(makefile, override_line),
                    )
                    self.write_minimal_make_checkout(hostile_checkout / "fake-root", "", "fake")
                    self.write(
                        hostile_checkout,
                        "scripts/repository_policy.py",
                        (repository_root / "scripts/repository_policy.py").read_text(encoding="utf-8"),
                    )
                    self.write(
                        hostile_checkout,
                        "scripts/check-baseline.py",
                        "from pathlib import Path\n"
                        "from repository_policy import inspect_repository\n"
                        "import sys\n"
                        "print('real policy authority')\n"
                        "failures = inspect_repository(Path(__file__).resolve().parents[1])\n"
                        "for failure in failures:\n"
                        "    print(failure, file=sys.stderr)\n"
                        "raise SystemExit(bool(failures))\n",
                    )

                    hostile_result = subprocess.run(
                        ["make", "test"],
                        cwd=hostile_checkout,
                        env=environment,
                        check=False,
                        capture_output=True,
                        text=True,
                    )

                    self.assertNotEqual(0, hostile_result.returncode, hostile_result.stdout)
                    self.assertIn("real policy authority", hostile_result.stdout)
                    self.assertIn("repository root independently", hostile_result.stderr)
                    self.assertNotIn("fake baseline", hostile_result.stdout)
                    self.assertNotIn("fake run-tests", hostile_result.stdout)

            hosted_checkout = temporary_root / "hosted-combined"
            hosted_checkout.mkdir()
            self.write_minimal_make_checkout(
                hosted_checkout,
                makefile
                + "\ncheck:\n\t@echo FAKE_CHECK_OVERRIDE\n"
                + "\ntest: override ROOT := $(CURDIR)/fake-root\n",
            )
            self.write_minimal_make_checkout(hosted_checkout / "fake-root", "", "fake")
            self.write(
                hosted_checkout,
                "scripts/repository_policy.py",
                (repository_root / "scripts/repository_policy.py").read_text(encoding="utf-8"),
            )
            self.write(
                hosted_checkout,
                "scripts/check-baseline.py",
                "from pathlib import Path\n"
                "from repository_policy import inspect_repository\n"
                "import sys\n"
                "print('real hosted policy authority')\n"
                "failures = inspect_repository(Path(__file__).resolve().parents[1])\n"
                "for failure in failures:\n"
                "    print(failure, file=sys.stderr)\n"
                "raise SystemExit(bool(failures))\n",
            )

            hosted_result = subprocess.run(
                ["/bin/sh", "-e", "-c", self.hosted_validation_command(repository_root)],
                cwd=hosted_checkout,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(0, hosted_result.returncode, hosted_result.stdout)
            self.assertIn("real hosted policy authority", hosted_result.stdout)
            self.assertIn("repository root independently", hosted_result.stderr)
            self.assertNotIn("FAKE_CHECK_OVERRIDE", hosted_result.stdout)
            self.assertNotIn("fake run-tests", hosted_result.stdout)

            shadow_checkout = temporary_root / "hosted-path-shadow"
            shadow_checkout.mkdir()
            self.write_minimal_make_checkout(shadow_checkout, makefile)
            self.write(
                shadow_checkout,
                "scripts/repository_policy.py",
                (repository_root / "scripts/repository_policy.py").read_text(encoding="utf-8"),
            )
            self.write(
                shadow_checkout,
                "scripts/check-baseline.py",
                "from pathlib import Path\n"
                "from repository_policy import inspect_repository\n"
                "import sys\n"
                "print('real hosted policy authority')\n"
                "failures = inspect_repository(Path(__file__).resolve().parents[1])\n"
                "for failure in failures:\n"
                "    print(failure, file=sys.stderr)\n"
                "raise SystemExit(bool(failures))\n",
            )
            self.write_executable(
                shadow_checkout,
                "scripts/run-tests.sh",
                (repository_root / "scripts/run-tests.sh").read_text(encoding="utf-8"),
            )
            self.write(
                shadow_checkout,
                "scripts/run-xcodebuild.py",
                (repository_root / "scripts/run-xcodebuild.py").read_text(encoding="utf-8"),
            )
            malicious_workflow = (repository_root / ".github/workflows/check.yml").read_text(
                encoding="utf-8"
            ).replace(
                "    runs-on: macos-15\n",
                "    runs-on: macos-15\n    env:\n      PATH: .:${{ env.PATH }}\n",
            )
            self.write(shadow_checkout, ".github/workflows/check.yml", malicious_workflow)
            (shadow_checkout / "Jenkins iOS Sample.xcodeproj").mkdir()
            fake_tool_log = shadow_checkout / "fake-native-tool-ran"
            for tool in ("xcrun", "xcodebuild"):
                self.write_executable(
                    shadow_checkout,
                    tool,
                    "#!/bin/sh\n"
                    "printf '%s\\n' {} >> {}\n"
                    "exit 0\n".format(tool, shlex.quote(str(fake_tool_log))),
                )
            shadow_environment = environment.copy()
            shadow_environment["PATH"] = ".{}{}".format(os.pathsep, shadow_environment["PATH"])
            shadow_environment["IOS_DESTINATION"] = "platform=iOS Simulator,id=TEST-DEVICE"

            shadow_result = subprocess.run(
                ["/bin/sh", "-e", "-c", self.hosted_validation_command(repository_root)],
                cwd=shadow_checkout,
                env=shadow_environment,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(0, shadow_result.returncode, shadow_result.stdout)
            self.assertIn("real hosted policy authority", shadow_result.stdout)
            self.assertIn("exact reviewed workflow", shadow_result.stderr)
            self.assertFalse(fake_tool_log.exists())

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
