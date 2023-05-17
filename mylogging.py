import logging
import logging.config
import yaml
from typing import Final
import os

DEFAULT_LEVEL: Final = logging.DEBUG


def log_setup(log_cfg_path: str='cfg.yaml', default_level=DEFAULT_LEVEL):
    """
    | Logging setup
    """
    if os.path.exists(log_cfg_path):
        with open(log_cfg_path, 'rt') as cfg_file:
            try:
                config = yaml.safe_load(cfg_file.read())
                logging.config.dictConfig(config)
            except Exception as e:
                print(e)
                print('Error with file, using Default logging')
                logging.basicConfig(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        print('Config file not found, using Default logging')
   