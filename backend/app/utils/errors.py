"""Custom exceptions for the application."""


class AppError(Exception):
    """Base application error."""

    def __init__(self, message, status_code=500, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Convert error to dictionary for JSON response."""
        rv = dict(self.payload or ())
        rv["error"] = self.message
        rv["status_code"] = self.status_code
        return rv


class ValidationError(AppError):
    """Validation error for invalid input."""

    def __init__(self, message, payload=None):
        super().__init__(message, status_code=400, payload=payload)


class NotFoundError(AppError):
    """Resource not found error."""

    def __init__(self, message="Resource not found", payload=None):
        super().__init__(message, status_code=404, payload=payload)


class ProcessingError(AppError):
    """Error during processing pipeline."""

    def __init__(self, message, stage=None, payload=None):
        payload = payload or {}
        if stage:
            payload["stage"] = stage
        super().__init__(message, status_code=500, payload=payload)
