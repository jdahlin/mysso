"""Settings for the SSO server."""

BASE_URL = "http://127.0.0.1:5000/"
JWT_ACCESS_TOKEN_LIFETIME = 60
JWT_REFRESH_TOKEN_LIFETIME = 3600
JWT_ALGORITHM = "ES256"
JWT_ISSUER = BASE_URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

