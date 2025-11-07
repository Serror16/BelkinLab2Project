LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "[%(asctime)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {"format": "%(asctime)s - %(levelname)s - %(message)s"},
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "src/shell.log",
            "encoding": "utf-8",
            "mode": "a",
            "formatter": "detailed",
            "level": "INFO",
        }
    },
    "loggers": {
        "shell_logger": {"handlers": ["file"], "level": "INFO", "propagate": False}
    },
}
