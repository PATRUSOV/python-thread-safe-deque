class LowThresholdError(Exception):
    """Exception raised when a value goes below the defined lower threshold."""


class HighThresholdError(Exception):
    """Exception raised when a value exceeds the defined upper threshold."""
