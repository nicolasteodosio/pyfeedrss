from .base import *  # noqa
from .base import env

SECRET_KEY = env("DJANGO_SECRET_KEY", default="TEST",)
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["test"] = ({"NAME": "test_db"},)
