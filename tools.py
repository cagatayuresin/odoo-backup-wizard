import platform
import subprocess
import os
from pathlib import Path


def clear_screen():
    if platform.system() == "Windows":
        subprocess.run("cls", shell=True)
    else:
        subprocess.run("clear", shell=True)


def open_folder_in_explorer(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.run(["open", path])
    elif platform.system() == "Linux":
        subprocess.run(["xdg-open", path])


def find_documents_folder():
    home = Path.home()
    try:
        documents = home / 'Documents'
        backup_path = documents / 'ODOOBackupWizard' / 'Backups'
        backup_path.mkdir(parents=True, exist_ok=True)
        return str(backup_path)
    except Exception as e:
        fallback_path = home / 'ODOOBackupWizard' / 'Backups'
        fallback_path.mkdir(parents=True, exist_ok=True)
        return str(fallback_path)
