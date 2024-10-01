import logging
from state_manager import StateManager

class WorkflowManager:
    def __init__(self, max_retries=3):
        self.retry_count = 0
        self.max_retries = max_retries
        self.aborted = False
        self.paused = False
        self.state_manager = StateManager()

        # Load existing state if available
        self.workflow_state = self.state_manager.load_state()

    def execute_task_with_retries(self, task_func, *args, **kwargs):
        """
        Executes a task function with retry logic and enhanced error handling.
        
        Args:
            task_func (function): The task function to execute.
            *args: Arguments for the task function.
            **kwargs: Keyword arguments for the task function.
        """
        while self.retry_count < self.max_retries and not self.aborted:
            try:
                if self.paused:
                    logging.info("Workflow is paused. Waiting...")
                    time.sleep(1)
                    continue

                logging.info(f"Executing task: {task_func.__name__} (Attempt {self.retry_count + 1}/{self.max_retries})")

                # Save the workflow state before starting
                self.state_manager.update_state("current_task", task_func.__name__)
                result = task_func(*args, **kwargs)
                
                if result:
                    logging.info(f"Task {task_func.__name__} completed successfully.")
                    self.retry_count = 0  # Reset retry count on success

                    # Save the state after successful completion
                    self.state_manager.update_state("last_successful_task", task_func.__name__)
                    return result
                else:
                    logging.warning(f"Task {task_func.__name__} failed. Retrying...")
                    self.retry_count += 1
            except Exception as e:
                logging.error(f"Error during {task_func.__name__}: {e}")
                self.retry_count += 1
                self.handle_error(e)

        logging.critical(f"Task {task_func.__name__} failed after {self.max_retries} attempts. Aborting workflow.")
        return False

    def handle_error(self, error):
        """
        Handle an error by logging context and presenting recovery options to the user.
        
        Args:
            error (Exception): The error that occurred.
        """
        # Save error state
        self.state_manager.update_state("error", str(error))
        logging.error(f"Handling error: {error}")