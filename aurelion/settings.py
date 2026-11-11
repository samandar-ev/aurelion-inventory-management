import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'

# The fallback key only exists so a fresh clone runs locally. Production
# (DEBUG off) refuses to start without a real key.
DEV_SECRET_KEY = 'django-insecure-local-development-only'
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY') or DEV_SECRET_KEY
if not DEBUG and SECRET_KEY == DEV_SECRET_KEY:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured('Set DJANGO_SECRET_KEY when DJANGO_DEBUG is False.')

ALLOWED_HOSTS_STR = os.getenv('DJANGO_ALLOWED_HOSTS', '')
if ALLOWED_HOSTS_STR:
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',') if host.strip()]
else:
    # Any host locally; only localhost in production until hosts are configured
    ALLOWED_HOSTS = ['*'] if DEBUG else ['localhost', '127.0.0.1']

CSRF_TRUSTED_ORIGINS_STR = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '')
if CSRF_TRUSTED_ORIGINS_STR:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in CSRF_TRUSTED_ORIGINS_STR.split(',') if origin.strip()]
else:
    CSRF_TRUSTED_ORIGINS = []

# Production cookie and header hardening (served over HTTPS behind the proxy)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.getenv('DJANGO_HSTS_SECONDS', '31536000'))
    if os.getenv('DJANGO_SECURE_PROXY_SSL_HEADER', 'False').lower() == 'true':
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'],
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aurelion.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'aurelion.wsgi.application'

# SQLite keeps the demo zero-config.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

def detect_system_timezone():
    """
    Pick up the local machine timezone (or env override) so displayed times
    match the host without hardcoding a region. Works across Linux/macOS/Windows
    when tzdata is available.
    """
    def _validate_tz(name):
        try:
            ZoneInfo(name)
            return name
        except Exception:
            return None

    env_tz = os.getenv('DJANGO_TIME_ZONE') or os.getenv('TZ')
    if env_tz and _validate_tz(env_tz):
        return env_tz

    def _from_path(path):
        try:
            real = os.path.realpath(path)
            parts = real.split(os.sep)
            tz_name = None
            for i, p in enumerate(parts):
                if p.startswith('zoneinfo') and i + 1 < len(parts):
                    tz_name = '/'.join(parts[i + 1 :])
                    break
            if tz_name and _validate_tz(tz_name):
                return tz_name
        except Exception:
            return None
        return None
    for candidate in ['/etc/localtime', '/var/db/timezone/localtime']:
        tz_name = _from_path(candidate)
        if tz_name:
            return tz_name
    try:
        with open('/etc/timezone', 'r') as fh:
            tz_name = fh.read().strip()
            if tz_name and _validate_tz(tz_name):
                return tz_name
    except Exception:
        pass
    try:
        # tzlocal handles Windows and Unix; returns canonical IANA names when tzdata is installed
        import tzlocal
        tz_name = tzlocal.get_localzone_name()
        if tz_name and _validate_tz(tz_name):
            return tz_name
    except Exception:
        pass
    try:
        tzinfo = datetime.now().astimezone().tzinfo
        tz_name = getattr(tzinfo, 'key', None) or getattr(tzinfo, 'zone', None) or tzinfo.tzname(None)
        if tz_name and _validate_tz(tz_name):
            return tz_name
    except Exception:
        pass
    return 'UTC'

TIME_ZONE = detect_system_timezone()

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'core.User'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'aurelion': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}
