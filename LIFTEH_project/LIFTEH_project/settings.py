import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Определяем среду выполнения
PRODUCTION = os.getenv('DJANGO_PRODUCTION', 'False').lower() == 'true'

# Яндекс Карты API ключ
YANDEX_MAPS_API_KEY = os.getenv(
    'YANDEX_MAPS_API_KEY', 'b0a03b93-14f2-4e5a-b38a-25ee1d5296e0')
SECRET_KEY = 'django-insecure-03alwk0(#3q^7&9v0i_!s+*bp-_)tspc7wsrrx1@gf02c-!3c('

if PRODUCTION:
    # Настройки для продакшена
    # SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
    DEBUG = False
    ALLOWED_HOSTS = ['jelezo.by', '178.159.242.118', 'www.jelezo.by']

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

    STATICFILES_DIRS = []
else:
    # Настройки для разработки
    # SECRET_KEY = 'django-insecure-03alwk0(#3q^7&9v0i_!s+*bp-_)tspc7wsrrx1@gf02c-!3c('
    DEBUG = True
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db_dev.sqlite3',
        }
    }

    # Для разработки - пути к статическим файлам
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static'),
    ]

# Общие настройки (одинаковые для всех сред)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'LIFTEH',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Добавляем whitenoise только в продакшене
if PRODUCTION:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

ROOT_URLCONF = 'LIFTEH_project.urls'

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

WSGI_APPLICATION = 'LIFTEH_project.wsgi.application'

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
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise настройки для лучшего обслуживания статики
if PRODUCTION:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

STATICFILES_IGNORE_PATTERNS = [
    'ico/*',
    '*.scss',
    '*.less',
    '*.map'
]
