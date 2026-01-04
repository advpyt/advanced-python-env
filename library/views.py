"""
View functions for the Library Management System.

These functions implement the core user interactions:
 - Displaying a list of books, optionally filtered by category.
 - Showing details of a single book.
 - Borrowing a book (logged-in users only).
 - Returning a borrowed book.
 - Viewing the borrowing history of the logged-in user.

The use of `@login_required` ensures that only authenticated users can
borrow or return books and view their history. Transactions are used
around borrow/return operations to ensure copy counts remain consistent.
"""

from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db import transaction
from .models import Book, Category, Borrow


def book_list(request):
    """Display a list of books with optional filtering by category."""
    category_id = request.GET.get("category")
    categories = Category.objects.all().order_by("name")
    books = Book.objects.select_related("category").all().order_by("title")

    if category_id:
        books = books.filter(category_id=category_id)

    return render(
        request,
        "library/book_list.html",
        {
            "books": books,
            "categories": categories,
            "selected_category": category_id,
        },
    )


def book_detail(request, pk: int):
    """Display the details of a single book."""
    book = get_object_or_404(Book.objects.select_related("category"), pk=pk)
    return render(request, "library/book_detail.html", {"book": book})


@login_required
@transaction.atomic
def borrow_book(request, pk: int):
    """Handle borrowing a book by the logged-in user."""
    if request.method != "POST":
        return redirect("book_detail", pk=pk)

    # Lock the book row for the duration of the transaction
    book = get_object_or_404(Book.objects.select_for_update(), pk=pk)
    if book.available_copies <= 0:
        return render(
            request,
            "library/error.html",
            {"message": "No copies available."},
        )

    Borrow.objects.create(
        borrower=request.user,
        book=book,
        due_date=Borrow.default_due_date(),
    )
    book.available_copies -= 1
    book.save(update_fields=["available_copies"])

    return redirect("my_history")


@login_required
@transaction.atomic
def return_book(request, borrow_id: int):
    """Handle returning a borrowed book by the logged-in user."""
    if request.method != "POST":
        return redirect("my_history")

    borrow = get_object_or_404(Borrow, pk=borrow_id, borrower=request.user)
    if borrow.returned_at is not None:
        return redirect("my_history")

    # Lock the associated book row
    book = Book.objects.select_for_update().get(pk=borrow.book_id)

    borrow.returned_at = timezone.now()
    borrow.save(update_fields=["returned_at"])

    book.available_copies += 1
    # Ensure we never exceed total_copies
    if book.available_copies > book.total_copies:
        book.available_copies = book.total_copies
    book.save(update_fields=["available_copies"])

    return redirect("my_history")


@login_required
def my_history(request):
    """Display the borrowing history of the logged-in user."""
    borrows = (
        Borrow.objects.select_related("book", "book__category")
        .filter(borrower=request.user)
        .order_by("-borrowed_at")
    )
    return render(request, "library/my_history.html", {"borrows": borrows})