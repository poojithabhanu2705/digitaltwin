from .settings import *

DATABASES["default"] = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": "test",
    "USER": "postgres",
    "PASSWORD": "postgres",
    "HOST": "localhost",
    "PORT": "5432",
}