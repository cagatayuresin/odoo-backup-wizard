"""Custom exception hierarchy for odoo-backup-wizard."""


class OdooBackupError(Exception):
    """Base exception for all odoo-backup-wizard errors."""


class ConnectionError(OdooBackupError):
    """Failed to connect to the Odoo server."""


class AuthenticationError(OdooBackupError):
    """Master password was rejected or server returned an error page."""


class BackupFormatError(OdooBackupError):
    """Server returned unexpected content type (not a binary file)."""


class StorageError(OdooBackupError):
    """Failed to write backup file to disk."""
