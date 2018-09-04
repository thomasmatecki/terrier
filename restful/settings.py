import os
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'hxh14t(lp=ueuu9xhveff9+z4g64dk088#_#*c*2^c(%huz^*j'
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
  #'django.contrib.admin',
  # 'django.contrib.auth',
  'django.contrib.contenttypes',
  'rest_framework',
  'flights'
  # 'django.contrib.sessions',
  # 'django.contrib.messages',
  # 'django.contrib.staticfiles',
  # 'api.apps.ApiConfig',
]

MIDDLEWARE = [
  # 'django.middleware.security.SecurityMiddleware',
  # 'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.common.CommonMiddleware',
  # 'django.middleware.csrf.CsrfViewMiddleware',
  # 'django.contrib.auth.middleware.AuthenticationMiddleware',
  # 'django.contrib.messages.middleware.MessageMiddleware',
  # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'restful.urls'

TEMPLATES = [
  {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'templates')]
    ,
    'APP_DIRS': True,
    'OPTIONS': {
      'context_processors': [
        # 'django.template.context_processors.debug',
        # 'django.template.context_processors.request',
        # 'django.contrib.auth.context_processors.auth',
        # 'django.contrib.messages.context_processors.messages',
      ],
    },
  },
]

WSGI_APPLICATION = 'restful.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
  'default': dj_database_url.parse('postgresql://django@127.0.0.1:5432/django')
}

#
# AUTH_PASSWORD_VALIDATORS = [
#   {
#     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#   },
#   {
#     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#   },
#   {
#     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#   },
#   {
#     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#   },
# ]

# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'
