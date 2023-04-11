"""Settings for the SSO server."""
import os
from pathlib import Path

source_dir = Path(__file__).parent.parent.parent
BASE_URL = "http://127.0.0.1:5000/"
OPENID_AUTHORIZATION_CODE_LIFETIME = 60

JWT_ACCESS_TOKEN_LIFETIME = 60
JWT_REFRESH_TOKEN_LIFETIME = 3600 * 24
JWT_ALGORITHM = "RS256"
JWT_ISSUER = BASE_URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
SQLALCHEMY_DATABASE_TEST_URL = "sqlite:///./sql_app_test.db"

# The password hashing algorith, see https://passlib.readthedocs.io/en/stable/narr/quickstart.html
# for a list of suggested algorithms for a new application
PASSWORD_HASH_SCHEME = "argon2"
PASSWORD_HASH_ROUNDS = 4

database_name = "sql_app_test" if os.environ.get("TESTING") else "sql_app"

DB_URL = f"sqlite:///{source_dir}/{database_name}.db"
