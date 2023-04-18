from authlib.oauth2.rfc6749 import InvalidRequestError
from authlib.oauth2.rfc7636 import CodeChallenge

from sso2.core.grants.authorization_code import MyAuthorizationCodeGrant


class MyCodeChallenge(CodeChallenge):  # type: ignore[misc]
    def validate_code_verifier(self, grant: MyAuthorizationCodeGrant) -> None:
        request = grant.request
        verifier = request.form.get("code_verifier")
        # public client MUST verify code challenge
        if (
            grant.is_code_challenge_required()
            and request.auth_method == "none"
            and not verifier
        ):
            raise InvalidRequestError('Missing "code_verifier"')
        super().validate_code_verifier(grant)
