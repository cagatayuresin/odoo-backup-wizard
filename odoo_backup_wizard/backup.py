"""Core backup logic for communicating with the Odoo database manager API."""

from __future__ import annotations

from datetime import datetime
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from odoo_backup_wizard.exceptions import (
    AuthenticationError,
    BackupFormatError,
    ConnectionError,
    StorageError,
)

if TYPE_CHECKING:
    from typing import Literal

logger = logging.getLogger(__name__)

_BACKUP_PATH = "/web/database/backup"
_CHUNK_SIZE = 8192  # bytes


def _normalize_url(url: str) -> str:
    """Normalize an Odoo server URL to the backup endpoint.

    Guarantees scheme is added before path manipulation so double-appending
    the path suffix is impossible regardless of input format.
    """
    url = url.rstrip("/")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    if not url.endswith(_BACKUP_PATH):
        url += _BACKUP_PATH
    return url


def _build_session(retries: int, verify_ssl: bool) -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.verify = verify_ssl
    return session


class BackupClient:
    """Client for performing Odoo database backups via the manager API."""

    def __init__(
        self,
        url: str,
        master_pwd: str,
        *,
        timeout: int = 300,
        retries: int = 3,
        verify_ssl: bool = True,
    ) -> None:
        self._endpoint = _normalize_url(url)
        self._master_pwd = master_pwd
        self._timeout = timeout
        self._session = _build_session(retries, verify_ssl)

    def backup(
        self,
        name: str,
        *,
        fileformat: Literal["zip", "dump"] = "zip",
        output_folder: Path | str = "backups",
    ) -> Path:
        """Download a backup of `name` database and save it to `output_folder`.

        Returns the path to the saved file.
        Raises OdooBackupError subclasses on all failure modes.
        """
        payload = {
            "master_pwd": self._master_pwd,
            "backup_format": fileformat,
            "name": name,
        }

        try:
            response = self._session.post(
                self._endpoint,
                data=payload,
                timeout=self._timeout,
                stream=True,
            )
            response.raise_for_status()
        except requests.exceptions.ConnectionError as exc:
            raise ConnectionError(f"Cannot reach Odoo server at {self._endpoint}: {exc}") from exc
        except requests.exceptions.HTTPError as exc:
            raise ConnectionError(f"HTTP error from Odoo server: {exc}") from exc
        except requests.exceptions.RequestException as exc:
            raise ConnectionError(f"Request failed: {exc}") from exc

        content_type = response.headers.get("Content-Type", "")
        if "text/html" in content_type:
            raise AuthenticationError(
                "Server returned an HTML page instead of a backup file. Check your master password."
            )
        if "application/octet-stream" not in content_type and "application/zip" not in content_type:
            logger.warning("Unexpected Content-Type '%s' — proceeding anyway", content_type)
            if not content_type or "text/" in content_type:
                raise BackupFormatError(
                    f"Unexpected Content-Type '{content_type}'. "
                    "The server did not return a binary file."
                )

        dest = Path(output_folder)
        try:
            dest.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise StorageError(f"Cannot create output folder '{dest}': {exc}") from exc

        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        file_path = dest / f"{name}-{timestamp}.{fileformat}"

        try:
            bytes_written = 0
            with file_path.open("wb") as fh:
                for chunk in response.iter_content(chunk_size=_CHUNK_SIZE):
                    fh.write(chunk)
                    bytes_written += len(chunk)
        except OSError as exc:
            raise StorageError(f"Failed to write backup file '{file_path}': {exc}") from exc

        logger.info(
            "Backup saved: %s (%.1f MB)",
            file_path,
            bytes_written / 1_048_576,
        )
        return file_path

    def delete_older_than(
        self,
        days: int,
        folder: Path | str = "backups",
    ) -> list[Path]:
        """Delete files in `folder` whose modification time is older than `days` days.

        Uses mtime (not ctime) so that file copies/rsync preserving timestamps
        are handled correctly on Linux.
        Returns a list of deleted paths.
        """
        now = datetime.now()
        deleted: list[Path] = []
        dest = Path(folder)

        if not dest.is_dir():
            logger.warning("Folder '%s' does not exist — nothing to delete", dest)
            return deleted

        for file_path in dest.iterdir():
            if not file_path.is_file():
                continue
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if (now - mtime).days > days:
                file_path.unlink()
                deleted.append(file_path)
                logger.info("Deleted old backup: %s", file_path.name)

        return deleted
