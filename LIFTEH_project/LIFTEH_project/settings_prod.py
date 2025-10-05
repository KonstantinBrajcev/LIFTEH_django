from .settings import *

ALLOWED_HOSTS = ['jelezo.by', '178.159.242.118', 'www.jelezo.by']
STATICFILES_DIRS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # Или любое другое имя
    }
}
