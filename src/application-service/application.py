import jwt
from flask import Flask, Response, abort, jsonify, request
from jwt import PyJWKClient

app = Flask(__name__)
APPLICATION_NAME = "application-service-1"
SSO_API_URL = "http://localhost:5000/"

jwks_client = PyJWKClient(f"{SSO_API_URL}/.well-known/jwks.json")
jwks_client.fetch_data()


@app.before_request
def before_request() -> None:
    header = request.headers.get("Authorization")
    if not header:
        abort(401)
        return
    token = header.split("Bearer ", 1)[1]
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    try:
        jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            issuer=SSO_API_URL,
            audience=APPLICATION_NAME,
        )
    except jwt.PyJWTError:
        abort(401)
    return None


@app.route("/protected_endpoint", methods=["GET"])
def protected_endpoint() -> Response:
    return jsonify({"secret-data": "very very secret"})


if __name__ == "__main__":
    app.run(port=5001, debug=True)
