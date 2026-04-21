import os
from pathlib import Path

from django.urls import reverse_lazy
from dotenv import load_dotenv

load_dotenv('.env')

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    "daphne",
    "channels",
    "jazzmin",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.apps.AppsConfig',

    'mptt',
    'django_filters',
    "django_json_widget",


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

ROOT_URLCONF = 'root.urls'

AUTH_USER_MODEL = 'apps.User'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.context_processors.regions_processor',
            ],
        },
    },
]


ASGI_APPLICATION = "root.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv('POSTGRES_NAME'),
        "USER": os.getenv('POSTGRES_USER'),
        "PASSWORD": os.getenv('POSTGRES_PASSWORD'),
        "HOST": os.getenv('POSTGRES_HOST'),
        "PORT": os.getenv('POSTGRES_PORT')
    }
}


AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')

LOGIN_URL = reverse_lazy('login_page')
LOGIN_REDIRECT_URL = reverse_lazy('profile_page')

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

JAZZMIN_SETTINGS = {
    "site_title": "OLX Uzbekistan Admin",
    "site_header": "OLX Uzbekistan",
    "site_brand": "OLX Uzbekistan",
    "site_logo": None,
    "login_logo": None,
    "login_logo_dark": None,
    "site_logo_classes": "img-circle",
    "site_icon": None,
    "welcome_sign": "Xush kelibsiz OLX Uzbekistan admin paneliga",
    "copyright": "OLX Uzbekistan Group Ltd",
    "search_model": ["apps.User", "apps.Announcement"],
    "user_avatar": "avatar",

    ############
    # Top Menu #
    ############
    "topmenu_links": [
        {"name": "Bosh sahifa", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"model": "apps.User"},
        {"model": "apps.Announcement"},
    ],

    #############
    # User Menu #
    #############
    "usermenu_links": [
        {"model": "apps.User"}
    ],

    #############
    # Side Menu #
    #############
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "apps", "apps.User", "apps.Announcement", "apps.Category", 
        "apps.Chat", "apps.Message", "apps.Region", "apps.District", 
        "apps.FavouriteAnnouncement"
    ],
    "icons": {
        "apps.User": "fas fa-user",
        "apps.Announcement": "fas fa-bullhorn",
        "apps.Category": "fas fa-list",
        "apps.Chat": "fas fa-comments",
        "apps.Message": "fas fa-envelope",
        "apps.Region": "fas fa-map-marker-alt",
        "apps.District": "fas fa-map-pin",
        "apps.FavouriteAnnouncement": "fas fa-heart",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    #################
    # Related Modal #
    #################
    "related_modal_active": True,

    #############
    # UI Tweaks #
    #############
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,

    ###############
    # Change view #
    ###############
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"apps.User": "collapsible", "apps.Announcement": "vertical_tabs"},
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "flatly",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

