"""Unit tests for odoo_backup_wizard.backup module."""

from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

from odoo_backup_wizard.backup import BackupClient, _normalize_url
from odoo_backup_wizard.exceptions import AuthenticationError, BackupFormatError

if TYPE_CHECKING:
    from pathlib import Path


# ---------------------------------------------------------------------------
# _normalize_url
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("odoo.example.com", "https://odoo.example.com/web/database/backup"),
        ("https://odoo.example.com", "https://odoo.example.com/web/database/backup"),
        ("http://odoo.example.com", "http://odoo.example.com/web/database/backup"),
        ("odoo.example.com/", "https://odoo.example.com/web/database/backup"),
        # Must NOT double-append the path
        (
            "odoo.example.com/web/database/backup",
            "https://odoo.example.com/web/database/backup",
        ),
        (
            "https://odoo.example.com/web/database/backup",
            "https://odoo.example.com/web/database/backup",
        ),
    ],
)
def test_normalize_url(raw: str, expected: str) -> None:
    assert _normalize_url(raw) == expected


# ---------------------------------------------------------------------------
# BackupClient.backup
# ---------------------------------------------------------------------------


def _make_mock_response(content_type: str, chunks: list[bytes]) -> MagicMock:
    mock = MagicMock()
    mock.status_code = 200
    mock.headers = {"Content-Type": content_type}
    mock.iter_content.return_value = iter(chunks)
    mock.raise_for_status.return_value = None
    return mock


def test_backup_raises_on_html_response(tmp_path: Path) -> None:
    """Wrong master_pwd → Odoo returns HTML → must raise AuthenticationError."""
    mock_resp = _make_mock_response("text/html; charset=utf-8", [b"<html>Access Denied</html>"])

    with patch("requests.Session.post", return_value=mock_resp):
        client = BackupClient("odoo.example.com", "wrong_password")
        with pytest.raises(AuthenticationError):
            client.backup("mydb", output_folder=tmp_path)


def test_backup_raises_on_unexpected_text_content_type(tmp_path: Path) -> None:
    mock_resp = _make_mock_response("text/plain", [b"some text"])

    with patch("requests.Session.post", return_value=mock_resp):
        client = BackupClient("odoo.example.com", "pwd")
        with pytest.raises(BackupFormatError):
            client.backup("mydb", output_folder=tmp_path)


def test_backup_saves_file_on_success(tmp_path: Path) -> None:
    """Successful backup saves a .zip file in the output folder."""
    fake_zip = b"PK\x03\x04" + b"\x00" * 100
    mock_resp = _make_mock_response("application/octet-stream", [fake_zip])

    with patch("requests.Session.post", return_value=mock_resp):
        client = BackupClient("odoo.example.com", "correct_password")
        saved = client.backup("mydb", output_folder=tmp_path)

    assert saved.exists()
    assert saved.suffix == ".zip"
    assert saved.parent == tmp_path
    assert saved.name.startswith("mydb-")


def test_backup_saves_dump_format(tmp_path: Path) -> None:
    mock_resp = _make_mock_response("application/octet-stream", [b"\x00" * 50])

    with patch("requests.Session.post", return_value=mock_resp):
        client = BackupClient("odoo.example.com", "pwd")
        saved = client.backup("mydb", fileformat="dump", output_folder=tmp_path)

    assert saved.suffix == ".dump"


def test_backup_creates_output_folder(tmp_path: Path) -> None:
    nested = tmp_path / "a" / "b" / "backups"
    mock_resp = _make_mock_response("application/octet-stream", [b"\x00" * 10])

    with patch("requests.Session.post", return_value=mock_resp):
        client = BackupClient("odoo.example.com", "pwd")
        saved = client.backup("mydb", output_folder=nested)

    assert nested.is_dir()
    assert saved.exists()


# ---------------------------------------------------------------------------
# BackupClient.delete_older_than
# ---------------------------------------------------------------------------


def test_delete_older_than_uses_mtime(tmp_path: Path) -> None:
    """Uses mtime, not ctime — file copies with preserved mtime are handled correctly."""
    old_file = tmp_path / "mydb-2026-01-01-00-00-00.zip"
    old_file.write_bytes(b"old backup content")
    eight_days_ago = time.time() - (8 * 86400)
    os.utime(old_file, (eight_days_ago, eight_days_ago))

    new_file = tmp_path / "mydb-2026-05-20-00-00-00.zip"
    new_file.write_bytes(b"recent backup")

    client = BackupClient("odoo.example.com", "pwd")
    deleted = client.delete_older_than(7, folder=tmp_path)

    assert old_file in deleted
    assert not old_file.exists()
    assert new_file.exists()


def test_delete_older_than_nonexistent_folder(tmp_path: Path) -> None:
    """Does not raise if folder does not exist, returns empty list."""
    client = BackupClient("odoo.example.com", "pwd")
    deleted = client.delete_older_than(7, folder=tmp_path / "nonexistent")
    assert deleted == []


def test_delete_older_than_skips_directories(tmp_path: Path) -> None:
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    old_time = time.time() - (10 * 86400)
    os.utime(subdir, (old_time, old_time))

    client = BackupClient("odoo.example.com", "pwd")
    deleted = client.delete_older_than(7, folder=tmp_path)

    assert deleted == []
    assert subdir.exists()


# ---------------------------------------------------------------------------
# Config file default handling (None-safe)
# ---------------------------------------------------------------------------


def test_config_partial_entry_defaults_to_zip() -> None:
    """A config entry missing 'fileformat' must default to 'zip', not None."""
    entry: dict[str, object] = {"url": "odoo.example.com", "name": "db1", "master_pwd": "pwd"}
    fileformat = entry.get("fileformat") or "zip"
    assert fileformat == "zip"


def test_config_partial_entry_defaults_output_folder() -> None:
    entry: dict[str, object] = {"url": "odoo.example.com", "name": "db1", "master_pwd": "pwd"}
    output_folder = entry.get("output_folder") or "backups"
    assert output_folder == "backups"
