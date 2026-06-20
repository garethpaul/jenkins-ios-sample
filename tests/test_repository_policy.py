import tempfile
import unittest
from pathlib import Path

from scripts.repository_policy import inspect_repository


class RepositoryPolicyTests(unittest.TestCase):
    def write(self, root, path, content):
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

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


if __name__ == "__main__":
    unittest.main()
