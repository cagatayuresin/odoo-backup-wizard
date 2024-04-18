import requests
import os
from datetime import datetime


class Backup:
    @staticmethod
    def backup(url, master_pwd, name, fileformat="zip", output_folder="backups"):
        if not url.endswith("/web/database/backup"):
            url += "/web/database/backup"
        if not url.startswith("http"):
            url = "https://" + url

        data = {
            "master_pwd": master_pwd,
            "backup_format": fileformat,
            "name": name,
        }
        try:
            response = requests.post(url, data=data)
        except requests.exceptions.RequestException as e:
            print(e)
            return False

        if response.status_code == 200:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)  # Eğer klasör yoksa oluştur

            file_path = os.path.join(
                output_folder, f"{name}-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.{fileformat}"
            )  # Dosyanın kaydedileceği tam yol

            with open(file_path, "wb") as f:
                f.write(response.content)  # İçeriği dosyaya yaz

            print(f"Backup request successful and saved to -> {file_path}")
            return True
        else:
            print("Backup request failed!")
            return False

    @staticmethod
    def delete_older_than(days, folder="backups"):
        now = datetime.now()
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if os.path.isfile(file_path):
                file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if (now - file_creation_time).days > days:
                    os.remove(file_path)
                    print(f"{file} deleted!")
