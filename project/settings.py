from pathlib import Path
import os
from django.core.management.utils import get_random_secret_key
import psycopg2
# Update database configuration from $DATABASE_URL.
import sys
import dj_database_url
from dotenv import load_dotenv
load_dotenv()
# by default django redirects the user after login to accounts/profile, even if you have different redirect in views
# if you want to change that use this next line
#LOGIN_REDIRECT_URL = '/accounts/username'
#LOGOUT_REDIRECT_URL = '/'
#LOGIN_URL = "/accounts/login/" # the same is /users/login/ because users redirect to accounts
# Application definition
INSTALLED_APPS = [ #  pip install django-phonenumber-field[phonenumbers
    'rest_framework',
    'account.apps.AccountConfig',
    "daphne",
    'chat',
    'django.contrib.admin',
    'django.contrib.auth', # Core authentication framework and its default models
    'django.contrib.contenttypes', # Django content type system (allows permissions to be associated with models).
    'django.contrib.sessions',
    'django.contrib.sites', # set of a single Django application/codebase with different sites (that can use different databases, logic in views, etc)
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'phonenumber_field',  # pip install django-phonenumber-field[phonenumberslite]
    'crispy_forms',
    "mailer",
    #'django_registration',
    'django_filters',
    # CORS
    'corsheaders',
    "django_bootstrap5",

    'blog.apps.BlogConfig', 
    'home.apps.HomeConfig', 
    'contact.apps.ContactConfig',
    'job.apps.JobConfig',
    #'pinax.notifications', # it causing ugettext problem in heroku becauseof requirements.txt(removed from both)
    'postman.apps.PostmanConfig', # either this or post man not both
    'ajax_select',
    #"messages", # it will clashes with postman.Message, so don't activate both, but just one and postman is the best ever
    'django_private_chat2.apps.DjangoPrivateChat2Config',
    'debug_toolbar', # after install pip3 install django-debug-toolbar
]
SITE_ID=1 
AUTH_USER_MODEL = 'account.User' # because we have extended user Model using a custome model in user app
ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window
MIDDLEWARE = [
    # CORS
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', # Manages sessions across requests
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware', # after pip3 install django-debug-toolbar
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Associates users with requests using sessions.
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = (
    'http://localhost:8080',
    'https://localhost:8080',
    "http://127.0.0.1:8080",
    "https://127.0.0.1:8080",
    'http://localhost:8000',
    'https://localhost:8000',
    "http://127.0.0.1:8000",
    "https://127.0.0.1:8000",
    "https://starfish-app-xgsam.ondigitalocean.app"
)
#CORS_ALLOWED_ORIGIN_REGEXES= # useful if you have many domains
CACHE_MIDDLEWARE_ALIAS = 'default' # The cache alias to use for storage
CACHE_MIDDLEWARE_SECONDS = 600 # The number of seconds each page should be cached for (TTL)


# The reason for setting a long-lived expiration time is to avoid problems
# in the case of a user closing a browser or bookmarking a page and then loading that page from a browser cache
# If the cache is shared across multiple sites using the same Django installation, set this to the name of the site
# or some other string that is unique to this Django instance, to prevent key collisions. Use an empty string if you don’t care
CACHE_MIDDLEWARE_KEY_PREFIX = ''  # name of site if multiple sites are used, should be used if the cache is shared across multiple sites that use the same Django instance
CRISPY_TEMPLATE_PACK = 'django-bootstrap5'
ROOT_URLCONF = 'project.urls'
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': ['127.0.0.1:11211', '0.0.0.0:11211'],
        'TIMEOUT': 200,
        'OPTIONS': {
            'no_delay': True,
            'ignore_exc': True,
            'max_pool_size': 4,
            'use_pooling': True,
        }
    },
    'redis': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': ['redis://127.0.0.1:6379', os.getenv("REDIS_URL"),],
        'OPTIONS': {
            'db': '0',
            'parser_class': 'redis.connection.PythonParser',
            'pool_class': 'redis.BlockingConnectionPool',
            # "CLIENT_CLASS": "django_redis.client.DefaultClient", # if you are using django-redis client rather than redis-py
            # that's already been instaled using => (pip install redis)
        }
    },
    'dummy': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

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
                #"messages.context_processors.user_messages", # i would use postman
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# In REST framework are all namespaced into a single dictionary setting, named REST_FRAMEWORK
# which helps keep them well separated from your other project settings
# You could also customize the pagination style 
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# Add to test email: display the email in the console in dev mode only
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = "mailer.backend.DbBackend"
# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS')

# Postman Settings
POSTMAN_I18N_URLS = True # True, if you want the internationalization of URL patterns, Defaults to: False
POSTMAN_DISALLOW_ANONYMOUS = True # True if you do not allow visitors to write to users, default is False
POSTMAN_DISALLOW_MULTIRECIPIENTS = False  # True if you do not allow more than one username in the recipient field, default is False.
POSTMAN_DISALLOW_COPIES_ON_REPLY = False # True if you do not allow additional recipients when replying, default is False.
POSTMAN_DISABLE_USER_EMAILING = False # True if you do not want basic email notification to users.
POSTMAN_NOTIFICATION_APPROVAL = 'account.views.notification_approval'
'''
POSTMAN_NOTIFICATION_APPROVAL => Defaults to: True.
The value can be specified as:
•	True to allow the sending in any case.
•	A function, with these parameters: user, action, site.
•	The full path to a function, as a string, whose import will be deferred. For example: 'account.views.myfunc'.
This sort of reference can be useful when resolving circular import dependencies between applications or modules.
The parameters of the function are: user, action, site.
•	The name of a method of a custom user model. The method is called on the user instance with these parameters: action, site.
•	(not recommended) Any other value that can be evaluated as a boolean and, if True, as a string.
'''
def get_from_email(context):
    return '<{} admin> no-reply@domain.tld'.format(context['action'])
POSTMAN_FROM_EMAIL = 'from@host.tld'   # get_from_email, default is DEFAULT_FROM_EMAIL
def get_params_email(context):
    return {
        'reply_to': ['someone@domain.tld'],
        'headers': {'X-my-choice': 'my-value'}
    } if context['action'] == 'acceptance' else {}
POSTMAN_PARAMS_EMAIL = get_params_email  # default is None
POSTMAN_AUTO_MODERATE_AS = True  # default is None
POSTMAN_SHOW_USER_AS = 'get_full_name' # lambda u: u.get_profile().nickname. like => progile.get_absolute_url()
POSTMAN_NAME_USER_AS = 'last_name'
POSTMAN_QUICKREPLY_QUOTE_BODY = True
#POSTMAN_NOTIFIER_APP = 'pinax_notifications' # must be activated but pinqx deprecated, so take it from site_packages to be an app
POSTMAN_MAILER_APP = 'mailer'
POSTMAN_AUTOCOMPLETER_APP = {'name': 'ajax_select', 'field': 'AutoCompleteField', 'arg_name': 'channel', 'arg_default': {}}

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = 'django-insecure-l_vqoi#zt$+h1$s7e2%$+$3++&jrhgm5+62n_g+6=^yanzqxa-'
#SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', get_random_secret_key())
SECRET_KEY = os.getenv("SECRET_KEY", get_random_secret_key()) # get_random_secret_key() supplied as default value
# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = False
DEBUG = os.getenv("DJANGO_DEBUG", "False") # causing problem not found for scripts and css
#ALLOWED_HOSTS = ['nagies.heroku.com', 'localhost', '127.0.0.1', '[::1]'] # ALLOWED_HOSTS = ['*']
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")
# ::1 is the compressed format IPV6 loopback address 0:0:0:0:0:0:0:1. It is the equivalent of the IPV4 address 127.0.0.1
# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

# using next methodsto test production db conection

# from django.core.exceptions import ImproperlyConfigured
# def get_env_value(env_variable):
#     try:
#         return os.environ[env_variable]
#     except KeyError:
#         error_msg = 'Set the {} environment variable'.format(env_variable)
#         raise ImproperlyConfigured(error_msg)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2', # django.db.backends.mysql'
#         'NAME': get_env_value('DB_NAME'), # DB Name os.environ['DATABASE_NAME'],
#         'USER': get_env_value('DB_USER'),  # from server register => connection tab change the name of server and username
#         'PASSWORD': get_env_value('DB_PASSWORD'),
#         'HOST': get_env_value('DB_URL'),    # os.environ['DATABASE_HOST'],
#         'PORT': get_env_value('DB_PORT'),  # int(os.environ['DATABASE_PORT']),
#     }
# }


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2', # django.db.backends.mysql'
#         'NAME': os.environ.get('DB_NAME'), # DB Name os.environ['PG_NAME'],
#         'USER': os.environ.get('DB_USER'),  # os.environ['PG_USER'], from server register => connection tab change the name of server and username
#         'PASSWORD': os.getenv('DB_PASSWORD'), # os.environ['PG_PASSWORD'], 
#         'HOST': os.environ.get('DB_HOST'), # remotely => dj_database_url.parse(os.environ.get("PG_HOST")), 
#         'PORT': os.environ.get('DB_PORT'),   # postgresql://USERNAME:PASSWORD@DB_HOST:DB_PORT/DATABASE_NAME
#     },
# }

DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "False") == "True"
# productions Settings
if DEVELOPMENT_MODE is True:
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # django.db.backends.mysql'
        'NAME': os.environ.get('PG_NAME'), # DB Name os.environ['PG_NAME'],
        'USER': os.environ.get('PG_USER'),  # os.environ['PG_USER'], from server register => connection tab change the name of server and username
        'PASSWORD': os.getenv('PG_PASSWORD'), # os.environ['PG_PASSWORD'], 
        'HOST': os.environ.get('PG_HOST'), # dj_database_url.parse(os.environ.get("DATABASE_URL")), 
        'PORT': os.environ.get('PG_PORT'),   # postgresql://USERNAME:PASSWORD@DB_HOST:DB_PORT/DATABASE_NAME
    },
    "test": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
elif len(sys.argv) > 0 and sys.argv[1] != 'collectstatic':
    if os.getenv("DB_URL", None) is None:
        raise Exception("DATABASE_URL environment variable not defined")
    DATABASES = {
        "default": dj_database_url.parse(os.environ.get("DB_URL")),
    }
    # or
    if "DB_URL" in os.environ:
        # Configure Django for DATABASE_URL environment variable.
        DATABASES["default"] = dj_database_url.config(conn_max_age=500, ssl_require=True)

    # Enable test database if found in CI environment.
    if "CI" in os.environ:
        DATABASES["default"]["TEST"] = DATABASES["default"]
    # # Update database configuration from $DATABASE_URL.
    # db_from_env = dj_database_url.config(conn_max_age=500)
    # DATABASES['default'].update(db_from_env)

# connection = psycopg2.connect(
#     host = 'your_RDB_AWS_instance_Endpoint',
#     port = 5432,
#     user = 'YOUR_USER_NAME',
#     password = 'YOUR_PASSWORD',
#     database='YOUR_DATABASE_NAME'
#     )
# cursor=connection.cursor()


# DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "True")
# # productions Settings
# if DEVELOPMENT_MODE == 'True':
#     DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2', # django.db.backends.mysql'
#         'NAME': os.environ.get('PG_NAME'), # DB Name os.environ['PG_NAME'],
#         'USER': os.environ.get('PG_USER'),  # os.environ['PG_USER'], from server register => connection tab change the name of server and username
#         'PASSWORD': os.getenv('PG_PASSWORD'), # os.environ['PG_PASSWORD'], 
#         'HOST': os.environ.get('PG_HOST'), # remotely => dj_database_url.parse(os.environ.get("PG_HOST")), 
#         'PORT': os.environ.get('PG_PORT'),   # postgresql://USERNAME:PASSWORD@DB_HOST:DB_PORT/DATABASE_NAME
#     },
#     "test": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
#     }
# }
# elif len(sys.argv) > 0 and sys.argv[1] != 'collectstatic':
#     if os.getenv("DB_URL", None) is None:
#         raise Exception("DATABASE_URL environment variable not defined")
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.postgresql_psycopg2', # django.db.backends.mysql'
#             'NAME': os.environ.get('DB_NAME'), # DB Name os.environ['PG_NAME'],
#             'USER': os.environ.get('DB_USER'),  # os.environ['PG_USER'], from server register => connection tab change the name of server and username
#             'PASSWORD': os.getenv('DB_PASSWORD'), # os.environ['PG_PASSWORD'], 
#             'HOST': os.environ.get('DB_URL'), # remotely => dj_database_url.parse(os.environ.get("DB_URL")), 
#             'PORT': os.environ.get('DB_PORT'),   # postgresql://USERNAME:PASSWORD@DB_HOST:DB_PORT/DATABASE_NAME
#         },
#     }
#     if "DB_URL" in os.environ:
#         # Configure Django for DATABASE_URL environment variable.
#         DATABASES["default"] = dj_database_url.config(conn_max_age=500, ssl_require=True)

#     # Enable test database if found in CI environment.
#     if "CI" in os.environ:
#         DATABASES["default"]["TEST"] = DATABASES["default"]

#     # # Update database configuration from $DATABASE_URL.
#     # db_from_env = dj_database_url.config(conn_max_age=500)
#     # DATABASES['default'].update(db_from_env)

# see Deployment checklist in how to deploy with wsgi file
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development') # development is the default valuew
if ENVIRONMENT == 'production':
    DEBUG = False
    SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())
    CSRF_COOKIE_AGE = 31449600 
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SESSION_EXPIRE_AT_BROWSER_CLOSE=True
    SECURE_HSTS_SECONDS = 10    # 31536000 it would break the site forlong time if you improperly set it, set it if everything is okay
    #SECURE_HSTS_PRELOAD=True
    SECURE_REDIRECT_EXEMPT = []
    USE_X_FORWARDED_HOST=True
    SECURE_SSL_REDIRECT = True # requests over HTTP will be redirected to HTTPS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..')
SITE_ROOT = PROJECT_ROOT / BASE_DIR # SITE_ROOT = BASE_DIR
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates" or '/127.0.0.1:8000/nagy/templates',
    # Always use forward slashes, even on Windows. "/path/to/my_project/my_app/static/bootstrap/",  
    # Don't forget to use absolute paths, not relative paths.
    # ("downloads", "/opt/webfiles/stats"),   tuple  prefix key or name of the path and value of the path
    os.path.join(SITE_ROOT, 'templates'),
)
# The absolute path to the directory where collectstatic will collect static files for deployment.
# The URL to use when referring to static files (where they will be served from)
STATIC_URL = '/static/' # then you can reach to all static from this url
#STATIC_ROOT = BASE_DIR / 'staticfiles'
#STATIC_ROOT = os.path.join(SITE_ROOT, 'static')
STATIC_ROOT = os.path.join(BASE_DIR, '_static') # for production use "/var/www/example.com/static/"
# Uncomment next line if you have extra static files and a directory in your GitHub repo.
# If you don't have this directory and have this uncommented your build will fail
# STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIAFILES_DIRS = (BASE_DIR / 'media')
# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# for using channels and websocket you need to have puip3 -m pip install channel_redis and then
ASGI_APPLICATION = "project.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.pubsub.RedisPubSubChannelLayer",  #   "channels_redis.core.RedisChannelLayer"
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379),  os.environ.get('REDIS_URL'),],
            # ['redis://127.0.0.1:6379', os.getenv("REDIS_URL"),],
            "on_disconnect": "redis.disconnect",
        },
    }, # you can add more channel layers here
}

