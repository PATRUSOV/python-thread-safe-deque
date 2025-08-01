class NoActiveTaskError(TypeError):
    """Raised when there is an attempt to mark a task done but no active tasks exist."""
