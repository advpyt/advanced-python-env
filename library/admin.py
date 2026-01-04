"""
Admin configuration for the Library Management System.

Registers the Category, Book and Borrow models with the Django admin
interface, enabling simple management of these objects from the
administration site.
"""

from django.contrib import admin

from .models import Category, Book, Borrow


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "total_copies",
        "available_copies",
    )
    list_filter = ("category",)
    search_fields = ("title", "author")


@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ("borrower", "book", "borrowed_at", "due_date", "returned_at")
    list_filter = ("returned_at",)
    search_fields = ("borrower__username", "book__title")