import enum
import http
from typing import NotRequired, TypedDict


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


class OAuth2ErrorCode(enum.StrEnum):
    """OAuth2 error codes."""

    INVALID_REQUEST = "invalid_request"
    UNAUTHORIZED_CLIENT = "unauthorized_client"
    ACCESS_DENIED = "access_denied"
    UNSUPPORTED_RESPONSE_TYPE = "unsupported_response_type"
    INVALID_SCOPE = "invalid_scope"
    SERVER_ERROR = "server_error"
    TEMPORARILY_UNAVAILABLE = "temporarily_unavailable"


# 4.1.2.1.  Error Response
class OAuth2ErrorResponseDict(TypedDict):
    error: str  # See OAuth2ErrorCode
    error_description: str
    error_uri: NotRequired[str]


class OAuth2Error(Exception):
    error_code: OAuth2ErrorCode

    def __init__(self, description: str, uri: str | None = None) -> None:
        self.description = description
        self.uri = uri

    def as_json(self) -> OAuth2ErrorResponseDict:
        content = OAuth2ErrorResponseDict(
            {
                "error": self.error_code,
                "error_description": self.description,
            },
        )
        if self.uri:
            content["error_uri"] = self.uri

        return content


class OAuth2InvalidRequestError(OAuth2Error):
    error_code = OAuth2ErrorCode.INVALID_REQUEST


class OAuth2UnauthorizedClientError(OAuth2Error):
    error_code = OAuth2ErrorCode.UNAUTHORIZED_CLIENT


class OAuth2AccessDeniedError(OAuth2Error):
    error_code = OAuth2ErrorCode.ACCESS_DENIED


class OAuth2UnsupportedResponseTypeError(OAuth2Error):
    error_code = OAuth2ErrorCode.UNSUPPORTED_RESPONSE_TYPE


class OAuth2InvalidScopeError(OAuth2Error):
    error_code = OAuth2ErrorCode.INVALID_SCOPE


class OAuth2ServerError(OAuth2Error):
    error_code = OAuth2ErrorCode.SERVER_ERROR


class OAuth2TemporarilyUnavailableError(OAuth2Error):
    error_code = OAuth2ErrorCode.TEMPORARILY_UNAVAILABLE
