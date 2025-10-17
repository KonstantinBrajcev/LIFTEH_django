import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Определяем среду выполнения
PRODUCTION = os.getenv('DJANGO_PRODUCTION', 'False').lower() == 'true'

# Яндекс Карты API ключ
YANDEX_MAPS_API_KEY = os.getenv(
    'YANDEX_MAPS_API_KEY', 'b0a03b93-14f2-4e5a-b38a-25ee1d5296e0')
SECRET_KEY = 'django-insecure-03alwk0(#3q^7&9v0i_!s+*bp-_)tspc7wsrrx1@gf02c-!3c('

# Настройки для API мониторинга автомобилей
TRACKER_API_LOGIN = 'NOVASTARTEH'
TRACKER_API_PASSWORD = 'NSTbelNST'

# ПОЛНОЕ ОТКЛЮЧЕНИЕ CORS - РАЗРЕШАЕМ ВСЁ
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['*']
CORS_ALLOW_HEADERS = ['*']
CORS_EXPOSE_HEADERS = ['*']
CORS_PREFLIGHT_MAX_AGE = 86400
X_FRAME_OPTIONS = 'ALLOWALL'

# Настройки для продакшена
if PRODUCTION:
    DEBUG = False
    ALLOWED_HOSTS = ['jelezo.by', '178.159.242.118', 'www.jelezo.by']
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    # ВАЖНО: Для продакшена STATIC_ROOT должен быть абсолютным путем
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Настройки для разработки
else:
    DEBUG = True
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db_dev.sqlite3',
        }
    }
    STATIC_ROOT = None  # В разработке не используем STATIC_ROOT

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Общие настройки
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'LIFTEH',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ДОБАВИТЬ ВСЕГДА
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'

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

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'