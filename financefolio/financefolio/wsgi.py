import os
from django.core.wsgi import get_wsgi_application

# Set the default Django settings module for the 'wsgi' application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financefolio.settings')

# Get the WSGI application for your project
application = get_wsgi_application()
