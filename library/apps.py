"""
App configuration for the Library application.

This configuration is used by Django to discover the application and
register its models with the ORM.
"""

from django.apps import AppConfig


class LibraryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "library"