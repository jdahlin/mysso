"""Token creation and validation."""
import uuid
from dataclasses import dataclass

from fastapi_sqlalchemy import db
from jwskate import Jwt, JwtSigner, SignedJwt
from pydantic import BaseModel

from sso.models import PersistentToken, Tenant, User
from sso.settings import (
    JWT_ACCESS_TOKEN_LIFETIME,
    JWT_REFRESH_TOKEN_LIFETIME,
    OPENID_AUTHORIZATION_CODE_LIFETIME,
)
from sso.ssotypes import Base64EncodedToken


@dataclass
class TokenContext:
    tenant: Tenant

    def create_authorization_code(
        self,
        user: User,
        lifetime: int = OPENID_AUTHORIZATION_CODE_LIFETIME,
    ) -> SignedJwt:
        tenant = self.tenant
        payload = {
            "exp": Jwt.timestamp() + lifetime,
            "iss": tenant.get_issuer(),
            "jti": str(uuid.uuid4()),
            "sub": user.id,
        }
        jwt = Jwt.sign(payload, jwk=tenant.get_private_key(), alg=tenant.algorithm)
        self._persist_jwt(jwt=jwt, user=user)
        return jwt

    def create_tokens(
        self,
        user: User,
        access_token_lifetime: int = JWT_ACCESS_TOKEN_LIFETIME,
        refresh_token_lifetime: int = JWT_REFRESH_TOKEN_LIFETIME,
    ) -> tuple[SignedJwt, SignedJwt]:
        tenant = self.tenant
        private_key = tenant.get_private_key()
        signer = JwtSigner(
            alg=tenant.algorithm,
            issuer=tenant.get_issuer(),
            jwk=private_key,
        )
        extra_headers = {"kid": private_key.public_jwk().thumbprint()}
        subject = str(user.id)
        access_token = signer.sign(
            extra_claims={"email": user.email},
            extra_headers=extra_headers,
            lifetime=access_token_lifetime,
            subject=subject,
        )
        refresh_token = signer.sign(
            extra_headers=extra_headers,
            lifetime=refresh_token_lifetime,
            subject=subject,
        )
        self._persist_jwt(jwt=refresh_token, user=user)
        return access_token, refresh_token

    def _persist_jwt(self, user: User, jwt: SignedJwt) -> None:
        refresh_token_expiration = PersistentToken(
            id=jwt.jwt_token_id,
            user=user,
            expires_at=jwt.expires_at,
        )
        db.session.add(refresh_token_expiration)
        db.session.commit()


class TokenPairResponse(BaseModel):
    access_token: Base64EncodedToken
    refresh_token: Base64EncodedToken
