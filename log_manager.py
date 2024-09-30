import logging

class LogManager:
    @staticmethod
    def configure_logger(log_file='flash_tool.log', level=logging.DEBUG):
        """
        Configures the logger with the specified level and log file.

        Args:
            log_file (str): Path to the log file.
            level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
        """
        logging.basicConfig(
            filename=log_file,
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filemode='w'
        )

    @staticmethod
    def change_log_level(level):
        """
        Dynamically change the log level during runtime.

        Args:
            level (int): New logging level (e.g., logging.DEBUG, logging.INFO).
        """
        logging.getLogger().setLevel(level)
        logging.info(f"Logging level changed to: {logging.getLevelName(level)}")
