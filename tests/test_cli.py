"""Unit tests for odoo_backup_wizard.cli module."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from odoo_backup_wizard import __version__
from odoo_backup_wizard.cli import _build_parser, _resolve_password, _run_from_config

if TYPE_CHECKING:
    from pathlib import Path


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    parser = _build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--version"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert __version__ in captured.out


def test_defaults() -> None:
    parser = _build_parser()
    args = parser.parse_args(["-u", "odoo.example.com", "-n", "mydb"])
    assert args.fileformat == "zip"
    assert args.output_folder == "backups"
    assert args.timeout == 300
    assert args.log_level == "INFO"
    assert not args.no_verify_ssl


def test_all_args_parsed() -> None:
    parser = _build_parser()
    args = parser.parse_args(
        [
            "-u",
            "odoo.example.com",
            "-n",
            "mydb",
            "-p",
            "s3cr3t",
            "-f",
            "dump",
            "-o",
            "/var/backups",
            "-d",
            "30",
            "--timeout",
            "120",
            "--no-verify-ssl",
            "--log-level",
            "DEBUG",
        ]
    )
    assert args.url == "odoo.example.com"
    assert args.name == "mydb"
    assert args.master_pwd == "s3cr3t"  # noqa: S105
    assert args.fileformat == "dump"
    assert args.output_folder == "/var/backups"
    assert args.delete_older_than == 30
    assert args.timeout == 120
    assert args.no_verify_ssl
    assert args.log_level == "DEBUG"


def test_invalid_fileformat() -> None:
    parser = _build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["-u", "x", "-n", "y", "-f", "tar"])


# ---------------------------------------------------------------------------
# _resolve_password
# ---------------------------------------------------------------------------


def test_resolve_password_from_arg() -> None:
    assert _resolve_password("mypassword") == "mypassword"


def test_resolve_password_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ODOO_MASTER_PWD", "env_secret")
    assert _resolve_password(None) == "env_secret"


def test_resolve_password_prompts_when_no_arg_no_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ODOO_MASTER_PWD", raising=False)
    with patch("getpass.getpass", return_value="prompted_pwd") as mock_getpass:
        result = _resolve_password(None)
    mock_getpass.assert_called_once()
    assert result == "prompted_pwd"


# ---------------------------------------------------------------------------
# Config file integration
# ---------------------------------------------------------------------------


def test_config_file_not_found_exits_2(tmp_path: Path) -> None:
    args = _build_parser().parse_args(["-u", "x", "-n", "y"])
    rc = _run_from_config(str(tmp_path / "nonexistent.json"), args)
    assert rc == 2


def test_config_file_runs_backup(tmp_path: Path) -> None:
    config = [
        {
            "url": "odoo.example.com",
            "name": "mydb",
            "master_pwd": "pwd",
            "fileformat": "zip",
            "output_folder": str(tmp_path),
        }
    ]
    config_path = tmp_path / "backup.json"
    config_path.write_text(json.dumps(config))

    mock_client = MagicMock()
    mock_client.backup.return_value = tmp_path / "mydb-2026-01-01.zip"

    args = _build_parser().parse_args(["-c", str(config_path)])

    with patch("odoo_backup_wizard.cli.BackupClient", return_value=mock_client):
        rc = _run_from_config(str(config_path), args)

    assert rc == 0
    mock_client.backup.assert_called_once()
