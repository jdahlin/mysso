from authlib.oauth2.rfc6749 import TokenMixin
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    ForeignKey,
    IntegerField,
    Model,
    TextField,
)

from sso2.core.models.user_model import User
from sso2.core.timeutils import now_timestamp


class OAuth2Token(Model, TokenMixin):  # type: ignore[misc]
    class Meta:
        verbose_name = "OAuth2 Token"
        verbose_name_plural = "OAuth2 Tokens"

    # null when using client_credentials grant
    user = ForeignKey(User, on_delete=CASCADE, null=True)
    client_id = CharField(max_length=48, db_index=True)
    token_type = CharField(max_length=40)
    access_token = CharField(max_length=255, unique=True, null=False)
    refresh_token = CharField(max_length=255, db_index=True)
    scope = TextField(default="")
    revoked = BooleanField(default=False)
    issued_at = IntegerField(null=False, default=now_timestamp)
    expires_in = IntegerField(null=False, default=0)

    def get_client_id(self) -> str:
        return self.client_id

    def get_scope(self) -> str:
        return self.scope

    def get_expires_in(self) -> int:
        return self.expires_in

    def get_expires_at(self) -> int:
        return self.issued_at + self.expires_in

    def is_expired(self) -> bool:
        return self.revoked or self.get_expires_at() < now_timestamp()

    def is_revoked(self) -> bool:
        return self.revoked
