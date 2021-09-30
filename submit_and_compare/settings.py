"""
Settings for submit_and_compare xblock
"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': 'intentionally-omitted',
    },
}
LOCALE_PATHS = [
    'submit_and_compare/translations',
]
SECRET_KEY = 'submit_and_compare_SECRET_KEY'

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
