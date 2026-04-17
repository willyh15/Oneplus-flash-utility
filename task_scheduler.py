import schedule
import time
import logging


class TaskScheduler:
    """
    Manages scheduled tasks and background processes for recurring operations.
    """

    @staticmethod
    def schedule_backup(interval="daily"):
        if interval == "daily":
            schedule.every().day.at("02:00").do(TaskScheduler.run_backup)
        elif interval == "weekly":
            schedule.every().monday.at("02:00").do(TaskScheduler.run_backup)

    @staticmethod
    def run_backup():
        logging.info("Running scheduled backup...")
        # Trigger the backup process
        # You can add the DeviceManager.backup_data_partition() method here
        logging.info("Scheduled backup completed successfully.")

    @staticmethod
    def start_scheduler():
        logging.info("Starting the task scheduler...")
        while True:
            schedule.run_pending()
            time.sleep(1)
