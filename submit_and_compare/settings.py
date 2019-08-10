"""
Settings for submit_and_compare xblock
"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': 'intentionally-omitted',
    },
}
SECRET_KEY = 'submit_and_compare_SECRET_KEY'
