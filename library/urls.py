"""
URL patterns for the Library application.

This module defines the mapping between URL paths and view functions for
all library‑related pages (catalog, book detail, borrowing and history).
"""
from django.urls import path

from . import views


app_name = "library"

urlpatterns: list = [
    path("", views.book_list, name="book_list"),
    path("books/<int:pk>/", views.book_detail, name="book_detail"),
    path("books/<int:pk>/borrow/", views.borrow_book, name="borrow_book"),
    path("borrows/<int:borrow_id>/return/", views.return_book, name="return_book"),
    path("library:my-history/", views.my_history, name="library:my_history"),
    # API endpoint for books
    path("api/books/", views.api_books, name="api_books"),
    # API endpoint for single book operations (GET, PUT, DELETE)
    path("api/books/<int:pk>/", views.api_book_detail, name="api_book_detail"),
]