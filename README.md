<a href="https://www.buymeacoffee.com/cagatayuresin" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="25"></a>
<a href="https://upload.wikimedia.org/wikipedia/commons/a/a7/Odoo_Official_Logo.png" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/a/a7/Odoo_Official_Logo.png" alt="Buy Me A Coffee" height="25"></a>

# Odoo Backup Wizard

Odoo Backup Wizard is a robust, cross-platform tool designed to automate the backup process for Odoo servers. This utility ensures your critical business data is safely backed up, supporting both GUI and CLI operations for versatile usability. The program is ideal for administrators and IT professionals managing Odoo deployments who need to ensure data integrity and availability with minimal effort.

## Key Features

- **Automated Backups:** Set up once and let Odoo Backup Wizard handle the rest, with scheduled backups that ensure your data is always up-to-date.
- **Cross-Platform Compatibility:** Whether you are running your Odoo on Windows, Linux, or macOS, Odoo Backup Wizard works seamlessly across all platforms.
- **GUI and CLI Support:** Use the graphical user interface for an intuitive experience or the command-line interface for automation and scripting.
- **Customizable Backup Paths:** Easily configure where your backups are stored, ensuring compatibility with your existing file management practices.
- **Simple Restoration Process:** Restoring from backups is just as straightforward, ensuring you can quickly recover from data loss events.

## Getting Started

To get started with Odoo Backup Wizard, please refer to the documentation available in this repository. Installation instructions, usage guidelines, and configuration details are all included to help you set up the tool according to your needs.

***

## Installation on Windows

<button name="win_cli_button" onclick="http://www.google.com">Download Windows CLI</button>
<button name="win_gui_button" onclick="http://www.google.com">Download Winows GUI </button>

## Usage

### CLI

```bash
python odoo_backup_wizard.py --help
```

```bash

 ██████╗ ██████╗  ██████╗  ██████╗     ██████╗  █████╗  ██████╗██╗  ██╗██╗   ██╗██████╗     ██╗    ██╗██╗███████╗ █████╗ ██████╗ ██████╗
██╔═══██╗██╔══██╗██╔═══██╗██╔═══██╗    ██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██║   ██║██╔══██╗    ██║    ██║██║╚══███╔╝██╔══██╗██╔══██╗██╔══██╗
██║   ██║██║  ██║██║   ██║██║   ██║    ██████╔╝███████║██║     █████╔╝ ██║   ██║██████╔╝    ██║ █╗ ██║██║  ███╔╝ ███████║██████╔╝██║  ██║
██║   ██║██║  ██║██║   ██║██║   ██║    ██╔══██╗██╔══██║██║     ██╔═██╗ ██║   ██║██╔═══╝     ██║███╗██║██║ ███╔╝  ██╔══██║██╔══██╗██║  ██║
╚██████╔╝██████╔╝╚██████╔╝╚██████╔╝    ██████╔╝██║  ██║╚██████╗██║  ██╗╚██████╔╝██║         ╚███╔███╔╝██║███████╗██║  ██║██║  ██║██████╔╝
 ╚═════╝ ╚═════╝  ╚═════╝  ╚═════╝     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝          ╚══╝╚══╝ ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝
Cagatay URESIN <cagatayuresin@gmail.com>                                                              v.1.0
https://github.com/cagatayuresin

usage: odoo_backup_wizard.py [-h] [--url URL] [-n NAME] [-p MASTER_PWD] [-f FILEFORMAT] [-o OUTPUT_FOLDER] [-d DELETE_OLDER_THAN] [-c CONFIG_FILE]

Odoo Database Backup Tool

options:
  -h, --help            show this help message and exit
  -u URL, --url URL     URL of the Odoo server
  -n NAME, --name NAME  DB Name
  -p MASTER_PWD, --master-pwd MASTER_PWD
                        Master Password
  -f FILEFORMAT, --fileformat FILEFORMAT
                        Format of the backup file
  -o OUTPUT_FOLDER, --output-folder OUTPUT_FOLDER
                        Output folder
  -d DELETE_OLDER_THAN, --delete-older-than DELETE_OLDER_THAN
                        Delete backups older than x days
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        Config file path (JSON)
```

### GUI

![GUI ss1](https://raw.githubusercontent.com/cagatayuresin/odoo-backup-wizard/master/resources/ss1.png "SS1")

![GUI ss2](https://raw.githubusercontent.com/cagatayuresin/odoo-backup-wizard/master/resources/ss2.png "SS2")

### Configuration File

The file must be in JSON format.

```json
[
  {
    "url": "odoo.example.com",
    "name": "db1",
    "master_pwd": "pwd1",
    "fileformat": "zip",
    "output_folder": "backups",
    "delete_older_than": 7
  },
  {
    "url": "odoo.example.com",
    "name": "db2",
    "master_pwd": "pwd2",
    "fileformat": "zip",
    "output_folder": "backups",
    "delete_older_than": 7
  },
  {
    "url": "odoo.example.com",
    "name": "db3",
    "master_pwd": "pwd3",
    "fileformat": "zip",
    "output_folder": "backups",
    "delete_older_than": 7
  }
]
```

## Contributing

We welcome contributions from the community! If you have suggestions, bug reports, or contributions, please submit them via issues or pull requests on this repository. Your input is invaluable in making Odoo Backup Wizard more effective and reliable.

## License

Copyright © 2024 [Cagatay URESIN](https:github.com/cagatayuresin)

Odoo Backup Wizard is released under the MIT License. See the LICENSE file in the repository for more details.