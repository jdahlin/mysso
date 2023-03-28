import http


class ServiceError(Exception):
    """Base class for all service errors."""

    status_code: http.HTTPStatus


class UnauthorizedError(ServiceError):
    """Raised when a user is not authorized."""

    status_code = http.HTTPStatus.UNAUTHORIZED


class BadRequestError(ServiceError):
    """Raised when an endpoint is called with the wrong parameters."""

    status_code = http.HTTPStatus.BAD_REQUEST


class UnsupportedGrantTypeError(BadRequestError):
    """Raised when an unsupported grant type is used."""


class EndpointNotImplementedError(ServiceError):
    """Raised when an endpoint is not implemented."""

    status_code = http.HTTPStatus.NOT_IMPLEMENTED
