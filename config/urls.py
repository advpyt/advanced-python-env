"""
URL configuration for the Library Management System.

This file routes incoming HTTP requests to the appropriate view. By default
it includes the built‑in Django admin interface and delegates the root
URL patterns to the `library` application.
"""
from django.contrib import admin
from django.urls import path, include


urlpatterns: list = [
    path("admin/", admin.site.urls),
    # Route root URL patterns to the library application
    path("", include("library.urls")),
]