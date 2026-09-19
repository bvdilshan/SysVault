import os
import tarfile
import json
from datetime import datetime

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def create_backup():
    config = load_config()
    dirs_to_backup = config.get("backup_dirs", [])
    dest_dir = config.get("backup_destination")


    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"system_backup_{timestamp}.tar.gz"
    archive_path = os.path.join(dest_dir, archive_name)

    print(f"Starting backup process -> {archive_path}")

    with tarfile.open(archive_path, "w:gz") as tar:
        for dir_path in dirs_to_backup:
            if os.path.exists(dir_path):
                print(f"Adding to backup: {dir_path}")
                tar.add(dir_path, arcname=os.path.basename(dir_path))
            else:
                print(f"Warning: Path not found - {dir_path}")

    print(f"Backup completed successfully: {archive_path}")
    return archive_path

if __name__ == "__main__":
    create_backup()