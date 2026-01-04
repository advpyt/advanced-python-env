#!/usr/bin/env python
"""
Utility script for administrative tasks in the Library Management System.

This file was generated manually because `django-admin startproject` is not
available in this environment. When run with the appropriate arguments it
delegates execution to Django's command‑line interface. You can use this
script to run the development server, perform database migrations and
interact with the project in other ways. See Django's documentation for
details.
"""
import os
import sys


def main() -> None:
    """Run administrative tasks."""
    # Default to using the settings module from the `config` package.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and available on your "
            "PYTHONPATH environment variable? Did you forget to activate a virtual "
            "environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()