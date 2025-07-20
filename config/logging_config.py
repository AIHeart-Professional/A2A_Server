import logging
import logging.config
import yaml
import os

def setup_logging(default_path='logging.yaml', default_level=logging.INFO):
    """
    Set up logging configuration from a YAML file.
    It constructs an absolute path to the config file, making it independent
    of the current working directory.
    """
    # Get the absolute path to the directory where this config file lives
    config_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(config_dir, default_path)

    if os.path.exists(path):
        try:
            with open(path, 'rt') as f:
                config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
        except Exception as e:
            logging.basicConfig(level=default_level)
            logging.warning(f"Error loading logging config from {path}: {e}. Using basic config.")
    else:
        logging.basicConfig(level=default_level)
        logging.warning(f"logging.yaml not found at {path}. Using basic config.")
