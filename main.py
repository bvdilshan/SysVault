import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from backup import create_backup, clean_local_old_backups
from sync import upload_to_s3, clean_s3_old_backups
from logger import logger

def main():
    logger.info("==========================================")
    logger.info("Automated System Backup & Sync Started")
    logger.info("==========================================")
    
    try:
        backup_file = create_backup()
        
        if backup_file:
            upload_success = upload_to_s3(backup_file)
            
            if upload_success:
                logger.info("Cloud synchronization completed successfully.")
            else:
                logger.error("Cloud synchronization failed.")
        else:
            logger.error("Backup archive creation failed. Aborting cloud sync.")

        logger.info("Running local and remote retention cleanup policies...")
        clean_local_old_backups()
        clean_s3_old_backups()

    except Exception as e:
        logger.critical(f"Unhandled failure during backup workflow: {e}", exc_info=True)

    logger.info("Automated System Backup & Sync Finished")
    logger.info("==========================================\n")

if __name__ == "__main__":
    main()