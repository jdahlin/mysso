"""Token creation and validation."""
from dataclasses import dataclass, field

from fastapi_sqlalchemy import db
from jwskate import Jwk, JwtSigner, SignedJwt
from pydantic import BaseModel

from sso.keys import get_private_key
from sso.models import RefreshTokenExpiration, User
from sso.settings import (
    JWT_ACCESS_TOKEN_LIFETIME,
    JWT_ALGORITHM,
    JWT_ISSUER,
    JWT_REFRESH_TOKEN_LIFETIME,
)
from sso.ssotypes import Audience, Base64EncodedToken


@dataclass
class TokenContext:
    user: User
    audience: Audience
    algorithm: str = JWT_ALGORITHM
    issuer: str = JWT_ISSUER
    private_key: Jwk = field(default_factory=get_private_key)
    access_token_lifetime: int = JWT_ACCESS_TOKEN_LIFETIME
    refresh_token_lifetime: int = JWT_REFRESH_TOKEN_LIFETIME

    def create_tokens(self) -> tuple[SignedJwt, SignedJwt]:
        signer = JwtSigner(
            alg=self.algorithm,
            issuer=self.issuer,
            jwk=self.private_key,
        )
        extra_headers = {"kid": self.private_key.public_jwk().thumbprint()}
        subject = str(self.user.id)
        access_token = signer.sign(
            audience=self.audience,
            extra_claims={"email": self.user.email},
            extra_headers=extra_headers,
            lifetime=self.access_token_lifetime,
            subject=subject,
        )
        refresh_token = signer.sign(
            extra_headers=extra_headers,
            lifetime=self.refresh_token_lifetime,
            subject=subject,
        )
        self.store_expiration(refresh_token=refresh_token)
        return access_token, refresh_token

    def store_expiration(self, refresh_token: SignedJwt) -> None:
        refresh_token_expiration = RefreshTokenExpiration(
            id=refresh_token.jwt_token_id,
            user=self.user,
            expires_at=refresh_token.expires_at,
            audience=self.audience,
        )
        db.session.add(refresh_token_expiration)
        db.session.commit()


class TokenPairResponse(BaseModel):
    access_token: Base64EncodedToken
    refresh_token: Base64EncodedToken
