import logging


class TaskLogger:
    def __init__(self, log_file="workflow_summary.log"):
        self.log_file = log_file
        self.tasks = []

    def start_task(self, task_name, retries=0):
        """Mark a task as started."""
        self.tasks.append(
            {"task_name": task_name, "status": "In Progress", "retries": retries}
        )
        self.log(f"Task '{task_name}' started. Retries: {retries}")

    def complete_task(self, task_name):
        """Mark a task as completed."""
        for task in self.tasks:
            if task["task_name"] == task_name:
                task["status"] = "Completed"
                self.log(f"Task '{task_name}' completed successfully.")
                break

    def fail_task(self, task_name, error_message, retries=0):
        """Mark a task as failed and update retry count."""
        for task in self.tasks:
            if task["task_name"] == task_name:
                task["status"] = f"Failed - {error_message}"
                task["retries"] = retries
                self.log(
                    f"Task '{task_name}' failed after {retries} retries. Error: {error_message}"
                )
                break

    def log(self, message):
        """Log a message to the summary file."""
        logging.info(message)
        with open(self.log_file, "a") as f:
            f.write(message + "\n")

    def generate_report(self):
        """Generate a detailed report of the workflow."""
        report_lines = ["Workflow Execution Summary:"]
        for task in self.tasks:
            report_lines.append(
                f"- {task['task_name']}: {task['status']} (Retries: {task['retries']})"
            )
        return "\n".join(report_lines)
