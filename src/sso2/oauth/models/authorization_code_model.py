import time

from authlib.oauth2.rfc6749 import AuthorizationCodeMixin
from django.db.models import (
    CASCADE,
    CharField,
    ForeignKey,
    IntegerField,
    Model,
    TextField,
)

from sso2.core.models.user_model import User
from sso2.core.timeutils import now_timestamp


class AuthorizationCode(Model, AuthorizationCodeMixin):  # type: ignore[misc]
    class Meta:
        verbose_name = "OAuth2 Authorization Code"
        verbose_name_plural = "OAuth2 Authorization Codes"

    user = ForeignKey(User, on_delete=CASCADE)
    client_id = CharField(max_length=48, db_index=True)
    code = CharField(max_length=120, unique=True, null=False)
    redirect_uri = TextField(default="", null=True)
    response_type = TextField(default="")
    scope = TextField(default="", null=True)
    auth_time = IntegerField(null=False, default=now_timestamp)

    nonce = CharField(max_length=120, default="", null=True)

    # See https://docs.authlib.org/en/latest/specs/rfc7636.html
    code_challenge = TextField(default="", null=True)
    code_challenge_method = TextField(default="", null=True)

    @classmethod
    def exists_nonce(cls, nonce: str, client_id: str) -> bool:
        try:
            cls.objects.get(client_id=client_id, nonce=nonce)
            return True
        except AuthorizationCode.DoesNotExist:
            return False

    def is_expired(self) -> bool:
        return self.auth_time + 300 < time.time()

    def get_redirect_uri(self) -> str | None:
        return self.redirect_uri

    def get_scope(self) -> str:
        return self.scope or ""

    def get_auth_time(self) -> int:
        return self.auth_time

    def get_nonce(self) -> str | None:
        return self.nonce
