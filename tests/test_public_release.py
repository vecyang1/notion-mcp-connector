from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "verify_public_release.py"


def load_auditor():
    spec = importlib.util.spec_from_file_location("verify_public_release", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.audit_directory


class PublicReleaseAuditTests(unittest.TestCase):
    def test_reports_live_secrets_and_private_locators_without_echoing_them(self) -> None:
        audit_directory = load_auditor()

        with tempfile.TemporaryDirectory() as temporary_directory:
            package = Path(temporary_directory)
            (package / "safe.md").write_text("Set NOTION_TOKEN in your environment.\n")
            (package / "unsafe.md").write_text(
                "\n".join(
                    [
                        "token=" + "ntn_" + "a" * 24,
                        "path=" + "/" + "Users/" + "person/private.env",
                        "database=" + "a" * 32,
                        "contact=" + "person@" + "private.example",
                    ]
                )
            )

            findings = audit_directory(package)

        self.assertEqual(
            findings,
            {
                "unsafe.md": [
                    "live Notion token",
                    "local-machine path",
                    "Notion-style identifier",
                    "non-example email address",
                ]
            },
        )

    def test_allows_documented_environment_variable_and_example_values(self) -> None:
        audit_directory = load_auditor()

        with tempfile.TemporaryDirectory() as temporary_directory:
            package = Path(temporary_directory)
            (package / "README.md").write_text(
                "\n".join(
                    [
                        "export NOTION_TOKEN=your_integration_token_here",
                        "Database ID: your-database-id-here",
                        "Contact: maintainer@example.com",
                    ]
                )
            )

            findings = audit_directory(package)

        self.assertEqual(findings, {})

    def test_ignores_generated_python_cache(self) -> None:
        audit_directory = load_auditor()

        with tempfile.TemporaryDirectory() as temporary_directory:
            package = Path(temporary_directory)
            generated = package / "__pycache__"
            generated.mkdir()
            (generated / "cache.pyc").write_text("path=" + "/" + "Users/" + "person/private.env")

            findings = audit_directory(package)

        self.assertEqual(findings, {})


if __name__ == "__main__":
    unittest.main()
