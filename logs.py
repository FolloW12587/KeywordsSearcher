from django.conf import settings


LOG_CONFIG = {
    "version": 1,
    'disable_existing_loggers': False,
    "root": {
        "handlers": ["console", "file", "info_file"],
        "level": "DEBUG" if settings.DEBUG else "INFO",
    },
    # "loggers": {
    #     ""
    # },
    "handlers": {
        "console": {
            "formatter": "std_out",
            "class": "logging.StreamHandler",
            "level": "DEBUG" if settings.DEBUG else "INFO",
        },
        "file": {
            "formatter": "file_formatter",
            "class": "logging.FileHandler",
            "filename": "logs/errors.log",
            "level": "ERROR"
        },
        "info_file": {
            "formatter": "file_formatter",
            "class": "logging.FileHandler",
            "filename": "logs/info.log",
            "level": "DEBUG" if settings.DEBUG else "INFO"
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
