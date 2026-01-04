"""
WSGI config for Library Management System.

This module exposes the WSGI callable as a module-level variable named
``application``. It is used by Django's runserver command and by any
WSGI-compatible web servers to serve your project.
"""

import os
from django.core.wsgi import get_wsgi_application

# Set the default settings module for the 'config' namespace
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Obtain the WSGI application object
application = get_wsgi_application()