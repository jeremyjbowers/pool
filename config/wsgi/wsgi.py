import os

deployment_environment = os.environ.get('DEPLOYMENT_ENVIRONMENT', None)
settings_file = "config.settings.development"

if deployment_environment in ['staging', 'production']:
    settings_file = "config.settings.production"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_file)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()