import argparse
import json
from request import Backup
from tools import clear_screen


LOGO = """
 ██████╗ ██████╗  ██████╗  ██████╗     ██████╗  █████╗  ██████╗██╗  ██╗██╗   ██╗██████╗     ██╗    ██╗██╗███████╗ █████╗ ██████╗ ██████╗ 
██╔═══██╗██╔══██╗██╔═══██╗██╔═══██╗    ██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██║   ██║██╔══██╗    ██║    ██║██║╚══███╔╝██╔══██╗██╔══██╗██╔══██╗
██║   ██║██║  ██║██║   ██║██║   ██║    ██████╔╝███████║██║     █████╔╝ ██║   ██║██████╔╝    ██║ █╗ ██║██║  ███╔╝ ███████║██████╔╝██║  ██║
██║   ██║██║  ██║██║   ██║██║   ██║    ██╔══██╗██╔══██║██║     ██╔═██╗ ██║   ██║██╔═══╝     ██║███╗██║██║ ███╔╝  ██╔══██║██╔══██╗██║  ██║
╚██████╔╝██████╔╝╚██████╔╝╚██████╔╝    ██████╔╝██║  ██║╚██████╗██║  ██╗╚██████╔╝██║         ╚███╔███╔╝██║███████╗██║  ██║██║  ██║██████╔╝
 ╚═════╝ ╚═════╝  ╚═════╝  ╚═════╝     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝          ╚══╝╚══╝ ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ 
Cagatay URESIN <cagatayuresin@gmail.com>                                                              v.1.0 
https://github.com/cagatayuresin
"""


def main():
    print(LOGO)
    parser = argparse.ArgumentParser(description="Odoo Database Backup Tool")
    parser.add_argument(
        "-u", "--url", type=str, help="URL of the Odoo server", required=False
    )
    parser.add_argument( "-n", "--name", type=str, help="DB Name", required=False)
    parser.add_argument("-p", "--master-pwd", type=str, help="Master Password", required=False)
    parser.add_argument(
        "-f",
        "--fileformat",
        type=str,
        default="zip",
        help="Format of the backup file",
        required=False,
    )
    parser.add_argument("-o", "--output-folder", type=str, default="backups", help="Output folder", required=False)
    parser.add_argument("-d", "--delete-older-than", type=int, help="Delete backups older than x days", required=False)
    parser.add_argument("-c", "--config-file", type=str, help="Config file path (JSON)", required=False)

    args = parser.parse_args()

    if args.config_file:
        with open(args.config_file, "r") as f:
            config = json.load(f)
            for db in config:
                args.url = db.get("url")
                args.name = db.get("name")
                args.master_pwd = db.get("master_pwd")
                args.fileformat = db.get("fileformat")
                args.output_folder = db.get("output_folder")
                args.delete_older_than = db.get("delete_older_than")
                result = Backup.backup(args.url, args.master_pwd, args.name, args.fileformat, args.output_folder)
                if result and args.delete_older_than:
                    Backup.delete_older_than(args.delete_older_than, args.output_folder)
        exit(0)
    else:
        running_via_args = any([args.url, args.name, args.master_pwd])
        url = args.url if args.url else input("Enter Odoo server URL: ")
        master_pwd = args.master_pwd if args.master_pwd else input("Master Password: ")
        name = args.name if args.name else input("Enter database name to backup: ")
        fileformat = (
            args.fileformat
            if running_via_args
            else input("Enter backup file format (zip/dump): ")
        )
        output_folder = args.output_folder if running_via_args else input("Enter output folder: ")

        result = Backup.backup(url, master_pwd, name, fileformat, output_folder)
        if result and args.delete_older_than:
            Backup.delete_older_than(args.delete_older_than, output_folder)
        if running_via_args:
            exit(0)


if __name__ == "__main__":
    while True:
        main()
        if input("Do you want to backup another database? (y/n): ").lower() != "y":
            break
        clear_screen()
