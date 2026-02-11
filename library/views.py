

from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db import transaction
from .models import Book, Category, Borrow
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json


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

    return redirect("library:my_history")


@login_required
@transaction.atomic
def return_book(request, borrow_id: int):
    """Handle returning a borrowed book by the logged-in user."""
    if request.method != "POST":
        return redirect("library:my_history")

    borrow = get_object_or_404(Borrow, pk=borrow_id, borrower=request.user)
    if borrow.returned_at is not None:
        return redirect("library:my_history")

    # Lock the associated book row
    book = Book.objects.select_for_update().get(pk=borrow.book_id)

    borrow.returned_at = timezone.now()
    borrow.save(update_fields=["returned_at"])

    book.available_copies += 1
    # Ensure we never exceed total_copies
    if book.available_copies > book.total_copies:
        book.available_copies = book.total_copies
    book.save(update_fields=["available_copies"])

    return redirect("library:my_history")


@login_required
def my_history(request):
    """Display the borrowing history of the logged-in user."""
    borrows = (
        Borrow.objects.select_related("book", "book__category")
        .filter(borrower=request.user)
        .order_by("-borrowed_at")
    )
    return render(request, "library/my_history.html", {"borrows": borrows})


# API endpoint to list and create books
@require_http_methods(["GET", "POST"])
@csrf_exempt
def api_books(request):
    """
    API endpoint that supports GET and POST operations on books.

    * GET: returns a list of books with their basic details in JSON format.
    * POST: accepts JSON payload to create a new book. Required fields are
      `title`, `author` and `category_id`. Optional field `total_copies` defaults to 1.
    """
    # GET request: return all books
    if request.method == "GET":
        books = Book.objects.select_related("category").all()
        data = [
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "category": book.category.name,
                "total_copies": book.total_copies,
                "available_copies": book.available_copies,
            }
            for book in books
        ]
        return JsonResponse(data, safe=False)

    # POST request: create a new book
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    title = payload.get("title")
    author = payload.get("author")
    category_id = payload.get("category_id")
    total_copies = payload.get("total_copies", 1)
    # Validate required fields
    if not title or not author or not category_id:
        return JsonResponse(
            {
                "error": "Missing required fields: title, author and category_id must be provided"
            },
            status=400,
        )
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return JsonResponse({"error": "Category not found"}, status=404)
    # Create the book
    book = Book.objects.create(
        title=title,
        author=author,
        category=category,
        total_copies=total_copies,
        available_copies=total_copies,
    )
    return JsonResponse(
        {
            "id": book.id,
            "message": "Book created successfully",
        },
        status=201,
    )


@require_http_methods(["GET", "PUT", "DELETE"])
@csrf_exempt
def api_book_detail(request, pk: int):
    """
    API endpoint to retrieve, update or delete a single book.

    * GET: return details for the specified book.
    * PUT: update a book's details using JSON payload. Supports updating
      `title`, `author`, `category_id`, and `total_copies`. When total_copies
      is reduced below the number of currently borrowed copies, the change is
      rejected.
    * DELETE: remove the book from the database if no copies are currently
      borrowed.
    """
    try:
        book = Book.objects.select_related("category").get(pk=pk)
    except Book.DoesNotExist:
        return JsonResponse({"error": "Book not found"}, status=404)

    # GET request: return the book details
    if request.method == "GET":
        data = {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "category": book.category.name,
            "category_id": book.category.id,
            "total_copies": book.total_copies,
            "available_copies": book.available_copies,
        }
        return JsonResponse(data)

    # PUT request: update book details
    if request.method == "PUT":
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON body"}, status=400)
        # Update simple string fields
        title = payload.get("title")
        author = payload.get("author")
        category_id = payload.get("category_id")
        total_copies = payload.get("total_copies")
        if title is not None:
            book.title = title
        if author is not None:
            book.author = author
        if category_id is not None:
            try:
                category = Category.objects.get(pk=category_id)
            except Category.DoesNotExist:
                return JsonResponse({"error": "Category not found"}, status=404)
            book.category = category
        if total_copies is not None:
            # Cannot set total copies below the number of borrowed copies
            borrowed_copies = book.total_copies - book.available_copies
            if total_copies < borrowed_copies:
                return JsonResponse(
                    {
                        "error": "total_copies cannot be less than the number of currently borrowed copies"
                    },
                    status=400,
                )
            # Adjust available_copies relative to change in total_copies
            diff = total_copies - book.total_copies
            book.total_copies = total_copies
            book.available_copies += diff
            # Ensure available_copies never negative
            if book.available_copies < 0:
                book.available_copies = 0
        # Save updates
        book.save()
        return JsonResponse({"message": "Book updated successfully"})

    # DELETE request: remove the book
    if request.method == "DELETE":
        # Only allow deletion if no copies are currently borrowed
        borrowed_copies = book.total_copies - book.available_copies
        if borrowed_copies > 0:
            return JsonResponse(
                {
                    "error": "Cannot delete book while copies are borrowed"
                },
                status=400,
            )
        book.delete()
        return JsonResponse({"message": "Book deleted successfully"}, status=204)


# ---------------------------------------------------------------------------
# Authentication views
#
# The following views provide simple registration and login pages that do not
# require the Django admin.  Users can create an account and sign in via
# the provided templates (see ``templates/library/register.html`` and
# ``templates/library/login.html``).  After successful registration or
# login, users are redirected to the main book list.

def register(request):
    """Register a new user.

    If the request is POST and the form is valid, a new user is created
    and automatically logged in.  The user is then redirected to the
    catalog page.  For GET requests, an empty ``UserCreationForm`` is
    presented.
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the new user in immediately after registration
            auth_login(request, user)
            return redirect("library:book_list")
    else:
        form = UserCreationForm()
    return render(request, "library/register.html", {"form": form})


def login_view(request):
    """Authenticate an existing user.

    Presents a login form.  If the user is already authenticated they
    are redirected to the catalog.  On POST, the form is validated and
    the user logged in; otherwise, the form with errors is re‑rendered.
    """
    if request.user.is_authenticated:
        return redirect("library:book_list")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect("library:book_list")
    else:
        form = AuthenticationForm()
    return render(request, "library/login.html", {"form": form})