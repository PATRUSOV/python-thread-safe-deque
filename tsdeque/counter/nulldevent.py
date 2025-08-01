class _NullDevent:
    """Stub implementation of Devent interface with no operational effect."""

    def set(self) -> None:
        """No-op method to match Devent interface."""

    def unset(self) -> None:
        """No-op method to match Devent interface."""


_NULL_DEVENT = _NullDevent()
