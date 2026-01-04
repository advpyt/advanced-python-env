"""
ASGI config for Library Management System.

This module exposes the ASGI callable as a module-level variable named
``application``. It is used by Django's asynchronous server interface and
supports asynchronous protocols such as WebSocket.
"""

import os
from django.core.asgi import get_asgi_application

# Set the default settings module for the project
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Get the ASGI application
application = get_asgi_application()