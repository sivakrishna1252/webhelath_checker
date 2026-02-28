"""
ASGI config for server_checker project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server_checker.settings')

application = get_asgi_application()
