import sys
import os

sys.path.append(os.path.dirname(__file__))

from backup import create_backup
from sync import upload_to_s3
from logger import logger

def main():
    logger.info("Automated Sytem Backup & Sync Started")
    
    try:
        backup_file = create_backup()
        logger.info(f"Backup archive created successfully: {backup_file}")
        upload_success = upload_to_s3(backup_file)
        
        if upload_success:
            logger.info("Cloud synchronization completed successfully.")
        else:
            logger.error("Cloud synchronization failed.")

    except Exception as e:
        logger.error(f"An unexpected error occurred during the backup process: {e}")

    logger.info("Automated System Backup & Sync Finished")

if __name__ == "__main__":
    main()