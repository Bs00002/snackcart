import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file for local development
load_dotenv()

try:
    import dj_database_url
except ImportError:
    dj_database_url = None

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    raise Exception("DJANGO_SECRET_KEY environment variable is not set.")

DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    ".vercel.app",
    ".onrender.com",
]

VERCEL_URL = os.environ.get("VERCEL_URL")
if VERCEL_URL:
    ALLOWED_HOSTS.append(VERCEL_URL)

# Handle Render hostname
render_hostname = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if render_hostname and render_hostname not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_hostname)

CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
]

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp1',
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

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'myproject.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

database_url = os.getenv('DATABASE_URL')
if database_url and dj_database_url is not None:
    DATABASES['default'] = dj_database_url.parse(database_url, conn_max_age=600, ssl_require=not DEBUG)

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'myapp1' / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend',
)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'snackcart@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'your-app-password')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', 'rzp_test_VQhEfe2NCXbbwI')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '2ibreCYL78DA3kjOhobCvz0f')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True


# ═══════════════════════════════════════════════════════════════════════════════
# JAZZMIN SETTINGS  —  SnackCart Admin Panel
# Brand colour: #FF6B35 (orange)  |  Dark: #1C1C2E  |  Accent: #27AE60
# ═══════════════════════════════════════════════════════════════════════════════
JAZZMIN_SETTINGS = {

    # ── Branding ──────────────────────────────────────────────────────────────
    "site_title":        "SnackCart Admin",
    "site_header":       "SnackCart",
    "site_brand":        "SnackCart",
    "site_logo":         None,           # e.g. "img/logo.png" once you add a logo
    "site_logo_classes": "img-circle",
    "site_icon":         None,           # favicon path e.g. "img/favicon.ico"
    "welcome_sign":      "Welcome to SnackCart Admin Panel",
    "copyright":         "SnackCart © 2026. All rights reserved.",
    "custom_css": "css/custom.css",

    # ── Search ────────────────────────────────────────────────────────────────
    "search_model": ["myapp1.User", "myapp1.Order", "myapp1.Product"],

    # ── Top-nav user menu ─────────────────────────────────────────────────────
    "user_avatar": None,

    # ── Top menu links ────────────────────────────────────────────────────────
    "topmenu_links": [
        {"name": "Dashboard",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Users",      "model": "myapp1.User"},
        {"name": "Orders",     "model": "myapp1.Order"},
        {"name": "Products",   "model": "myapp1.Product"},
        {"name": "View Site",  "url": "/", "new_window": True},
    ],

    # ── User menu (top-right dropdown) ────────────────────────────────────────
    "usermenu_links": [
        {"name": "View Site", "url": "/", "new_window": True},
    ],

    # ── Sidebar ───────────────────────────────────────────────────────────────
    "show_sidebar":             True,
    "navigation_expanded":      True,
    "hide_apps":                [],
    "hide_models":              [],

    # Sidebar icon map  (Font Awesome 5 free icons)
    "icons": {
        # Auth
        "auth":                     "fas fa-users-cog",
        "auth.user":                "fas fa-user-shield",
        "auth.Group":               "fas fa-users",
        # SnackCart models
        "myapp1.User":              "fas fa-user",
        "myapp1.SellerProfile":     "fas fa-store",
        "myapp1.Subscription":      "fas fa-crown",
        "myapp1.Category":          "fas fa-tags",
        "myapp1.Product":           "fas fa-utensils",
        "myapp1.CustomerAddress":   "fas fa-map-marker-alt",
        "myapp1.Order":             "fas fa-shopping-bag",
        "myapp1.Review":            "fas fa-star",
        "myapp1.Complaint":         "fas fa-exclamation-circle",
        "myapp1.Inquiry":           "fas fa-envelope-open-text",
        "myapp1.Contact":           "fas fa-headset",
    },
    "default_icon_parents":  "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    # ── Sidebar grouping / ordering ───────────────────────────────────────────
    "order_with_respect_to": [
        "myapp1",
        "myapp1.User",
        "myapp1.SellerProfile",
        "myapp1.Subscription",
        "myapp1.Category",
        "myapp1.Product",
        "myapp1.CustomerAddress",
        "myapp1.Order",
        "myapp1.Review",
        "myapp1.Complaint",
        "myapp1.Inquiry",
        "myapp1.Contact",
        "auth",
    ],

    # ── Related-modal popups ──────────────────────────────────────────────────
    "related_modal_active": True,

    # ── Custom CSS / JS ───────────────────────────────────────────────────────
    # Uncomment below once you create these files in myapp1/static/
    # "custom_css": "css/admin_custom.css",
    # "custom_js":  "js/admin_custom.js",

    # ── Other UI options ──────────────────────────────────────────────────────
    "show_ui_builder":         False,   # set True temporarily to tweak colours live
    "changeform_format":       "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user":  "collapsible",
        "auth.group": "vertical_tabs",
    },

    # ── Language chooser ──────────────────────────────────────────────────────
    "language_chooser": False,
}


# ═══════════════════════════════════════════════════════════════════════════════
# JAZZMIN UI TWEAKS  —  colour scheme matching SnackCart brand (#FF6B35 orange)
# ═══════════════════════════════════════════════════════════════════════════════
JAZZMIN_UI_TWEAKS = {

    # ── Theme base ─────────────────────────────────────────────────────────────
    # AdminLTE skin options:
    #   "skin_blue" | "skin_blue_light" | "skin_black" | "skin_black_light"
    #   "skin_purple" | "skin_purple_light" | "skin_green" | "skin_green_light"
    #   "skin_red" | "skin_red_light" | "skin_yellow" | "skin_yellow_light"
    # We use "skin_black" as the base, then override with custom CSS vars below
    "navbar_small_text":   False,
    "footer_small_text":   False,
    "body_small_text":     False,
    "brand_small_text":    False,

    # ── Colour overrides ──────────────────────────────────────────────────────
    # These map to AdminLTE / Bootstrap class names that Jazzmin exposes
    "brand_colour":        "navbar-orange",   # see custom CSS below
    "accent":              "accent-warning",  # closest built-in to orange

    # Navbar
    "navbar":              "navbar-dark",
    "no_navbar_border":    True,
    "navbar_fixed":        True,

    # Sidebar
    "sidebar":             "sidebar-dark-warning",  # dark sidebar, orange accents
    "sidebar_nav_small_text":  False,
    "sidebar_disable_expand":  False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style":  False,
    "sidebar_nav_flat_style":    False,

    # ── Layout ────────────────────────────────────────────────────────────────
    "theme":               "darkly",   # Bootswatch theme — dark, modern look
    # Available: default | cerulean | cosmo | cyborg | darkly | flatly
    #            journal | litera  | lumen | lux    | materia | minty
    #            pulse   | sandstone | simplex | sketchy | slate | solar
    #            spacelab | superhero | united | yeti

    "dark_mode_theme":     "darkly",   # same theme in dark mode toggle

    # ── Buttons & actions ─────────────────────────────────────────────────────
    "button_classes": {
        "primary":   "btn-warning",     # orange-ish in Bootswatch darkly
        "secondary": "btn-outline-secondary",
        "info":      "btn-info",
        "warning":   "btn-warning",
        "danger":    "btn-danger",
        "success":   "btn-success",
    },

    # ── Actions & filters ─────────────────────────────────────────────────────
    "actions_sticky_top": True,
}
