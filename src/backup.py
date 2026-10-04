import os
import tarfile
import json
import time
from datetime import datetime
from logger import logger

def load_config():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'config', 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found at: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format in config file: {e}")
        return {}

def create_backup():
    config = load_config()
    dirs_to_backup = config.get("backup_dirs", [])
    dest_dir = config.get("backup_destination")

    if not dest_dir:
        logger.error("Backup destination path missing in configuration.")
        return None

    try:
        os.makedirs(dest_dir, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create destination directory {dest_dir}: {e}")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"system_backup_{timestamp}.tar.gz"
    archive_path = os.path.join(dest_dir, archive_name)

    logger.info(f"Starting backup process -> {archive_path}")

    try:
        with tarfile.open(archive_path, "w:gz") as tar:
            added_any = False
            for dir_path in dirs_to_backup:
                
                if os.path.exists(dir_path):
                    logger.info(f"Adding to backup archive: {dir_path}")
                    tar.add(dir_path, arcname=os.path.basename(dir_path))
                    added_any = True
                else:
                    logger.warning(f"Path not found, skipping: {dir_path}")

            if not added_any:
                logger.warning("No valid source directories were found to back up.")

        logger.info(f"Backup archive created successfully: {archive_path}")
        return archive_path

    except Exception as e:
        logger.error(f"Failed to create backup archive: {e}")
        if os.path.exists(archive_path):
            os.remove(archive_path)
        return None

def clean_local_old_backups():
    """Removes local archives older than retention_days."""
    config = load_config()
    dest_dir = config.get("backup_destination")
    retention_days = config.get("retention_days", 7)
    if not dest_dir or not os.path.exists(dest_dir):
        return

    now = time.time()
    cutoff = now - (retention_days * 86400) 

    for filename in os.listdir(dest_dir):
        if filename.startswith("system_backup_") and filename.endswith(".tar.gz"):
            filepath = os.path.join(dest_dir, filename)
            try:
                if os.path.getmtime(filepath) < cutoff:
                    os.remove(filepath)
                    logger.info(f"Local Retention Policy: Purged old backup -> {filename}")
            except Exception as e:
                logger.error(f"Failed to delete old local backup {filename}: {e}")