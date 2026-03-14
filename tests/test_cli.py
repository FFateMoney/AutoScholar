from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from autoscholar.cli import app

runner = CliRunner()


def test_workspace_init_and_doctor(tmp_path: Path) -> None:
    workspace_dir = tmp_path / "citation-demo"
    result = runner.invoke(
        app,
        [
            "workspace",
            "init",
            str(workspace_dir),
            "--template",
            "citation-paper",
            "--reports-lang",
            "zh",
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert (workspace_dir / "workspace.yaml").exists()

    doctor = runner.invoke(app, ["workspace", "doctor", "--workspace", str(workspace_dir)])
    assert doctor.exit_code == 0, doctor.stdout


def test_schema_export(tmp_path: Path) -> None:
    output_dir = tmp_path / "schemas"
    result = runner.invoke(app, ["schema", "export", "--output-dir", str(output_dir)])
    assert result.exit_code == 0, result.stdout
    assert (output_dir / "workspace_manifest.schema.json").exists()
