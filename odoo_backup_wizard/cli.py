"""Command-line interface for odoo-backup-wizard."""

from __future__ import annotations

import argparse
import getpass
import json
import logging
import os
from pathlib import Path
import sys
from typing import Any

from odoo_backup_wizard import __version__
from odoo_backup_wizard.backup import BackupClient
from odoo_backup_wizard.exceptions import (
    AuthenticationError,
    BackupFormatError,
    ConnectionError,
    OdooBackupError,
    StorageError,
)

# Exit codes — documented in README so shell scripts can rely on them.
_EXIT_OK = 0
_EXIT_BACKUP_FAILED = 1
_EXIT_CONFIG_NOT_FOUND = 2
_EXIT_AUTH_ERROR = 3
_EXIT_CONNECTION_ERROR = 4

_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        level=getattr(logging, level.upper()),
    )


def _resolve_password(args_value: str | None) -> str:
    """Resolve master password: CLI arg > ODOO_MASTER_PWD env var > interactive prompt."""
    if args_value:
        return args_value
    env_pwd = os.environ.get("ODOO_MASTER_PWD")
    if env_pwd:
        return env_pwd
    return getpass.getpass("Master password: ")


def _run_single(
    client: BackupClient,
    name: str,
    fileformat: str,
    output_folder: str,
    delete_older_than: int | None,
) -> int:
    try:
        saved = client.backup(name, fileformat=fileformat, output_folder=output_folder)  # type: ignore[arg-type]
        logging.getLogger(__name__).info("Done: %s", saved)
    except AuthenticationError as exc:
        logging.getLogger(__name__).error("Authentication failed: %s", exc)
        return _EXIT_AUTH_ERROR
    except ConnectionError as exc:
        logging.getLogger(__name__).error("Connection error: %s", exc)
        return _EXIT_CONNECTION_ERROR
    except (BackupFormatError, StorageError, OdooBackupError) as exc:
        logging.getLogger(__name__).error("Backup failed: %s", exc)
        return _EXIT_BACKUP_FAILED

    if delete_older_than is not None:
        client.delete_older_than(delete_older_than, folder=output_folder)

    return _EXIT_OK


def _run_from_config(config_path: str, args: argparse.Namespace) -> int:
    path = Path(config_path)
    if not path.exists():
        logging.getLogger(__name__).error("Config file not found: %s", config_path)
        return _EXIT_CONFIG_NOT_FOUND

    with path.open(encoding="utf-8") as fh:
        config: list[dict[str, Any]] = json.load(fh)

    overall_exit = _EXIT_OK
    for entry in config:
        url = entry.get("url", "")
        name = entry.get("name", "")
        master_pwd = entry.get("master_pwd", "")
        fileformat = entry.get("fileformat") or "zip"
        output_folder = entry.get("output_folder") or "backups"
        delete_older_than = entry.get("delete_older_than")

        if master_pwd:
            logging.getLogger(__name__).warning(
                "Config contains plaintext master_pwd for '%s'. "
                "Consider using ODOO_MASTER_PWD environment variable instead.",
                name,
            )

        client = BackupClient(
            url,
            master_pwd,
            timeout=args.timeout,
            verify_ssl=not args.no_verify_ssl,
        )
        rc = _run_single(client, name, fileformat, output_folder, delete_older_than)
        if rc != _EXIT_OK:
            overall_exit = rc

    return overall_exit


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="odoo-backup-wizard",
        description="Back up Odoo databases via the database manager API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit codes:
  0  Success
  1  Backup failed (unexpected error)
  2  Config file not found
  3  Authentication error (wrong master password)
  4  Connection error (server unreachable)

Environment variables:
  ODOO_MASTER_PWD   Master password (overridden by --master-pwd)

Examples:
  odoo-backup-wizard -u odoo.example.com -n mydb
  odoo-backup-wizard -u odoo.example.com -n mydb -f dump -o /var/backups/odoo -d 30
  odoo-backup-wizard -c /etc/odoo-backup.json
""",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-u", "--url", help="Odoo server URL")
    parser.add_argument("-n", "--name", help="Database name to back up")
    parser.add_argument(
        "-p", "--master-pwd", dest="master_pwd", help="Master password (or set ODOO_MASTER_PWD)"
    )
    parser.add_argument(
        "-f",
        "--fileformat",
        choices=["zip", "dump"],
        default="zip",
        help="Backup file format (default: zip)",
    )
    parser.add_argument(
        "-o",
        "--output-folder",
        dest="output_folder",
        default="backups",
        help="Destination folder (default: ./backups)",
    )
    parser.add_argument(
        "-d",
        "--delete-older-than",
        dest="delete_older_than",
        type=int,
        metavar="DAYS",
        help="Delete backups older than DAYS days from the output folder",
    )
    parser.add_argument("-c", "--config-file", dest="config_file", help="JSON config file path")
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        metavar="SECONDS",
        help="HTTP request timeout in seconds (default: 300)",
    )
    parser.add_argument(
        "--no-verify-ssl",
        dest="no_verify_ssl",
        action="store_true",
        help="Disable SSL certificate verification",
    )
    parser.add_argument(
        "--log-level",
        dest="log_level",
        choices=_LOG_LEVELS,
        default="INFO",
        help="Logging level (default: INFO)",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    _configure_logging(args.log_level)

    if args.config_file:
        sys.exit(_run_from_config(args.config_file, args))

    if not args.url:
        parser.error("--url is required (or use --config-file)")
    if not args.name:
        parser.error("--name is required (or use --config-file)")

    master_pwd = _resolve_password(args.master_pwd)
    client = BackupClient(
        args.url,
        master_pwd,
        timeout=args.timeout,
        verify_ssl=not args.no_verify_ssl,
    )
    sys.exit(
        _run_single(client, args.name, args.fileformat, args.output_folder, args.delete_older_than)
    )


if __name__ == "__main__":
    main()
