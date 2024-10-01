import json
import logging
import os

class StateManager:
    def __init__(self, state_file='workflow_state.json'):
        self.state_file = state_file
        self.state = {}

    def save_state(self, state_data):
        """
        Save the current workflow state to a JSON file.
        
        Args:
            state_data (dict): Dictionary representing the workflow state.
        """
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state_data, f, indent=4)
            logging.info(f"Workflow state saved successfully to {self.state_file}.")
        except Exception as e:
            logging.error(f"Failed to save workflow state: {e}")

    def load_state(self):
        """
        Load the workflow state from the JSON file.
        
        Returns:
            dict: The loaded state data. Returns an empty dictionary if not found.
        """
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
                logging.info(f"Workflow state loaded successfully from {self.state_file}.")
            except json.JSONDecodeError as e:
                logging.error(f"Failed to decode workflow state file: {e}")
                self.state = {}
        else:
            logging.warning(f"No state file found at {self.state_file}. Starting fresh.")
            self.state = {}
        return self.state

    def update_state(self, key, value):
        """
        Update a specific state attribute and save.
        
        Args:
            key (str): The attribute key to update.
            value: The new value for the attribute.
        """
        self.state[key] = value
        self.save_state(self.state)

    def clear_state(self):
        """
        Clear the saved state to reset the workflow.
        """
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
            logging.info(f"State file {self.state_file} cleared.")
        self.state = {}