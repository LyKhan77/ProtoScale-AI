"""Structured logging configuration."""
import logging
import sys
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "job_id"):
            log_data["job_id"] = record.job_id

        if hasattr(record, "stage"):
            log_data["stage"] = record.stage

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return str(log_data)


def get_logger(name):
    """Get a configured logger."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
