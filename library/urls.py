"""
URL patterns for the Library application.

This module defines the mapping between URL paths and view functions for
all library‑related pages (catalog, book detail, borrowing and history).
"""
from django.urls import path

from . import views
from django.contrib.auth import views as auth_views


app_name = "library"

urlpatterns: list = [
    path("", views.book_list, name="book_list"),
    path("books/<int:pk>/", views.book_detail, name="book_detail"),
    path("books/<int:pk>/borrow/", views.borrow_book, name="borrow_book"),
    path("borrows/<int:borrow_id>/return/", views.return_book, name="return_book"),
    path("my-history/", views.my_history, name="my_history"),
    # API endpoint for books
    path("api/books/", views.api_books, name="api_books"),
    # API endpoint for single book operations (GET, PUT, DELETE)
    path("api/books/<int:pk>/", views.api_book_detail, name="api_book_detail"),

    # Authentication routes.  The login and registration pages provide
    # separate views for users to authenticate without relying on the
    # Django admin.  The logout view uses the built‑in Django
    # ``LogoutView`` to handle session termination.
    path("accounts/register/", views.register, name="register"),
    path("accounts/login/", views.login_view, name="login"),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(next_page="library:book_list"),
        name="logout",
    ),
]