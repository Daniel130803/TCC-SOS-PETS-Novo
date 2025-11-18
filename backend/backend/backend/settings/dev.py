from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Em dev, liberar CORS para facilitar o desenvolvimento
CORS_ALLOW_ALL_ORIGINS = True
