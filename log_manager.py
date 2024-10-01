import logging
from logging.handlers import RotatingFileHandler

class LogManager:
    """
    Manages log configuration, log rotation, and custom log messages.
    """
    log_file = 'flash_tool.log'
    max_bytes = 5 * 1024 * 1024  # 5 MB
    backup_count = 3

    @staticmethod
    def configure_logger():
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        # Create a rotating file handler
        handler = RotatingFileHandler(LogManager.log_file, maxBytes=LogManager.max_bytes,
                                      backupCount=LogManager.backup_count)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        logging.info("Log Manager configured successfully.")