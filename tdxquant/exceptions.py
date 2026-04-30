class TdxQuantError(Exception):
    """Base exception for trading adapter failures."""


class UnsupportedPlatformError(TdxQuantError):
    """Raised when a Windows-only operation is requested on another platform."""
