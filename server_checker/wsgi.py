"""
WSGI config for server_checker project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server_checker.settings')

application = get_wsgi_application()
