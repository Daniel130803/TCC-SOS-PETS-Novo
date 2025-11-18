from .base import *  # noqa

DEBUG = False

# Segurança adicional para produção
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# CORS restrito via env
CORS_ALLOW_ALL_ORIGINS = False
# Configure via env: CORS_ALLOWED_ORIGINS="https://app.exemplo.com,https://www.exemplo.com"

# Hosts definidos via env (no base)
