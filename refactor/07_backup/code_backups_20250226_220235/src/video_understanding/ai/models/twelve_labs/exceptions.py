"""Exceptions for TwelveLabs model."""

from ...exceptions import ModelError, ValidationError


class TwelveLabsError(ModelError):
    """Base exception for TwelveLabs-related errors."""

    pass


class TwelveLabsAPIError(TwelveLabsError):
    """Exception raised when TwelveLabs API returns an error."""

    pass


class TwelveLabsAuthError(TwelveLabsError):
    """Exception raised for authentication errors.

    :no-index:
    """

    pass


class TwelveLabsRateLimitError(TwelveLabsError):
    """Exception raised when API rate limits are exceeded.

    :no-index:
    """

    pass


class TwelveLabsTimeoutError(TwelveLabsError):
    """Exception raised when API requests timeout.

    :no-index:
    """

    pass


class TwelveLabsValidationError(ValidationError):
    """Exception raised when TwelveLabs input validation fails."""

    pass


class TwelveLabsConfigError(TwelveLabsError):
    """Exception raised for configuration errors.

    :no-index:
    """

    pass


class TwelveLabsProcessingError(TwelveLabsError):
    """Exception raised for video processing errors.

    :no-index:
    """

    pass


# Alias for backward compatibility
APITimeoutError = TwelveLabsTimeoutError
