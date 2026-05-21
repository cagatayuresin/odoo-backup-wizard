<a href="https://www.odoo.com" target="_blank"><img src="https://raw.githubusercontent.com/cagatayuresin/odoo-backup-wizard/master/resources/odoo_logo.png" alt="Odoo" height="25"></a>
<a href="https://www.buymeacoffee.com/cagatayuresin" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="25"></a>

![CI](https://github.com/cagatayuresin/odoo-backup-wizard/actions/workflows/ci.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/odoo-backup-wizard)
![Python](https://img.shields.io/pypi/pyversions/odoo-backup-wizard)
![License](https://img.shields.io/github/license/cagatayuresin/odoo-backup-wizard)

# Odoo Backup Wizard

A cross-platform CLI tool that automates Odoo database backups via the built-in
database manager API (`/web/database/backup`). Designed for system administrators
who run Odoo on Linux and need reliable, scriptable, cron-friendly backups.

## Key Features

- **Single-command backups** — one line to download a `.zip` or `.dump`
- **Batch backups** — back up multiple databases in one run via a JSON config file
- **Backup retention** — automatically delete backups older than N days
- **Cron-ready** — structured log output, meaningful exit codes, no interactive prompts
- **Secure** — master password from env var, SSL verification, warns on plaintext passwords
- **Retry logic** — automatic retry with exponential back-off on transient server errors
- **Zero bloat** — single runtime dependency (`requests`)

---

## Installation

```bash
pip install odoo-backup-wizard
```

Or install from source:

```bash
git clone https://github.com/cagatayuresin/odoo-backup-wizard.git
cd odoo-backup-wizard
pip install -e .
```

---

## Quick Start

```bash
# Back up a single database
odoo-backup-wizard -u odoo.example.com -n mydb

# Specify format, output folder, and retention policy
odoo-backup-wizard -u odoo.example.com -n mydb -f dump -o /var/backups/odoo -d 30

# Use a JSON config file for multiple databases
odoo-backup-wizard -c /etc/odoo-backup.json
```

---

## Options

```text
Usage: odoo-backup-wizard [OPTIONS]

Options:
  -u, --url URL               Odoo server URL
  -n, --name NAME             Database name to back up
  -p, --master-pwd PWD        Master password (or set ODOO_MASTER_PWD)
  -f, --fileformat {zip,dump} Backup file format [default: zip]
  -o, --output-folder DIR     Destination folder [default: ./backups]
  -d, --delete-older-than N   Delete backups older than N days
  -c, --config-file FILE      JSON config file (supports multiple databases)
      --timeout SECONDS       HTTP timeout in seconds [default: 300]
      --no-verify-ssl         Disable SSL certificate verification
      --log-level LEVEL       DEBUG | INFO | WARNING | ERROR [default: INFO]
      --version               Show version and exit
  -h, --help                  Show this message and exit
```

---

## Security

Avoid passing the master password on the command line (it appears in `ps` output and shell history).
Use the environment variable instead:

```bash
export ODOO_MASTER_PWD="your_master_password"
odoo-backup-wizard -u odoo.example.com -n mydb
```

Priority order: `--master-pwd` > `ODOO_MASTER_PWD` > interactive prompt.

---

## Exit Codes

| Code | Meaning                                      |
| ---- | -------------------------------------------- |
| 0    | Success                                      |
| 1    | Backup failed (unexpected error)             |
| 2    | Config file not found                        |
| 3    | Authentication error (wrong master password) |
| 4    | Connection error (server unreachable)        |

Shell scripting example:

```bash
if odoo-backup-wizard -u odoo.example.com -n mydb; then
    echo "Backup OK"
else
    echo "Backup FAILED with exit code $?" >&2
fi
```

---

## Cron Job

```cron
# /etc/cron.d/odoo-backup
# Back up all production databases at 02:00 every night, keep 30 days
0 2 * * * odoo-user ODOO_MASTER_PWD=secret odoo-backup-wizard -c /etc/odoo-backup.json
```

Or with a dedicated env file:

```bash
# /etc/cron.d/odoo-backup
ODOO_MASTER_PWD=secret
0 2 * * * odoo-user odoo-backup-wizard -c /etc/odoo-backup.json
```

---

## Configuration File

Use a JSON config file to back up multiple databases in one run.
All fields except `url`, `name`, and `master_pwd` are optional.

```json
[
  {
    "url": "odoo.example.com",
    "name": "production",
    "master_pwd": "pwd1",
    "fileformat": "zip",
    "output_folder": "/var/backups/odoo/production",
    "delete_older_than": 30
  },
  {
    "url": "odoo.example.com",
    "name": "staging",
    "master_pwd": "pwd2",
    "fileformat": "dump",
    "output_folder": "/var/backups/odoo/staging",
    "delete_older_than": 7
  }
]
```

**Security note:** config files with plaintext `master_pwd` will trigger a WARNING.
Prefer the `ODOO_MASTER_PWD` environment variable.

---

## Development

```bash
git clone https://github.com/cagatayuresin/odoo-backup-wizard.git
cd odoo-backup-wizard
pip install -e ".[dev]"

# Lint + format
ruff check .
ruff format .

# Type check
mypy odoo_backup_wizard

# Tests with coverage
pytest --cov=odoo_backup_wizard

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

---

## Contributing

Issues and pull requests are welcome. Please run `ruff check .` and `pytest` before submitting.

## License

Copyright © 2024 [Cagatay URESIN](https://github.com/cagatayuresin)

Released under the [MIT License](LICENSE).
