import logging

class StateManager:
    """
    Manages the internal state of the application.
    Provides state tracking and validation to ensure
    processes run under correct conditions.
    """

    _current_state = None

    @staticmethod
    def set_state(state):
        logging.info(f"State changed to: {state}")
        StateManager._current_state = state

    @staticmethod
    def get_state():
        return StateManager._current_state

    @staticmethod
    def validate_state(expected_state):
        if StateManager._current_state != expected_state:
            logging.error(f"Invalid state. Expected {expected_state}, but got {StateManager._current_state}")
            raise RuntimeError(f"Invalid state. Expected {expected_state}, but got {StateManager._current_state}")
        else:
            logging.info(f"State validated: {expected_state}")