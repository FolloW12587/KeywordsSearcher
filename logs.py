import os
from logging import config

import config as cfg


LOG_CONFIG = {
    "version": 1,
    "root": {
        "handlers": ["console", "file", "info_file"],
        "level": "DEBUG" if cfg.DEBUG else "INFO",
    },
    "handlers": {
        "console": {
            "formatter": "std_out",
            "class": "logging.StreamHandler",
            "level": "DEBUG" if cfg.DEBUG else "INFO",
        },
        "file": {
            "formatter": "file_formatter",
            "class": "logging.FileHandler",
            "filename": "logs.errors.log",
            "level": "ERROR"
        },
        "info_file": {
            "formatter": "file_formatter",
            "class": "logging.FileHandler",
            "filename": "logs.info.log",
            "level": "DEBUG" if cfg.DEBUG else "INFO"
        }
    },
    "formatters": {
        "std_out": {
            "format": '%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s'
        },
        "file_formatter": {
            "format": '%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s'
        }
    }
}

config.dictConfig(LOG_CONFIG)