from .base import *  # noqa
from .base import env

SECRET_KEY = env("DJANGO_SECRET_KEY", default="TEST",)
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["test"] = ({"NAME": "test_db"},)

DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.stub.StubBroker",
    "OPTIONS": {},
    "MIDDLEWARE": [
        "dramatiq.middleware.AgeLimit",
        "dramatiq.middleware.TimeLimit",
        "dramatiq.middleware.Callbacks",
        "dramatiq.middleware.Pipelines",
        "dramatiq.middleware.Retries",
        "django_dramatiq.middleware.AdminMiddleware",
        "django_dramatiq.middleware.DbConnectionsMiddleware",
    ],
}

DRAMATIQ_MAX_RETRIES = 0

# WhiteNoise
INSTALLED_APPS = ["whitenoise.runserver_nostatic"] + INSTALLED_APPS  # noqa F405
