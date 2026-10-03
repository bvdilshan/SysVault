import os
import logging

def setup_logger():
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../logs'))
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, 'backup.log')

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger("BackupDaemon")

logger = setup_logger()