import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Безопасность - лучше вынести в переменные окружения
SECRET_KEY = 'django-insecure-03alwk0(#3q^7&9v0i_!s+*bp-_)tspc7wsrrx1@gf02c-!3c('

# Дебаг по умолчанию False для безопасности
DEBUG = True

# Пустые хосты по умолчанию (переопределяются в local/prod)
ALLOWED_HOSTS = ['jelezo.by', '178.159.242.118', 'www.jelezo.by']

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

LANGUAGE_CODE = 'ru-ru'  # Изменено на русский
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Путь к статическим файлам
STATIC_URL = '/static/'

# Путь к директории, где будут собираться статические файлы
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Медиа файлы (если нужны)
# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

INTERNAL_IPS = ['127.0.0.1']

