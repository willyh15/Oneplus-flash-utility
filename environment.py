import os


class Environment:
    """
    Manages the application's environment variables, paths, and sensitive data.
    """

    @staticmethod
    def get_env_var(variable_name, default=None):
        return os.getenv(variable_name, default)

    @staticmethod
    def set_env_var(variable_name, value):
        os.environ[variable_name] = value

    @staticmethod
    def list_all_env_vars():
        return dict(os.environ)
