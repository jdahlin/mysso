import os

from .dev import *
from .dev import BASE_DIR, DATABASES

DEBUG = True
DATABASES["default"]["NAME"] = BASE_DIR / "db-test.sqlite3"
os.environ["AUTHLIB_INSECURE_TRANSPORT"] = "true"
