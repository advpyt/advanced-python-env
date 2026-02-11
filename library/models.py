"""
Database models for the Library Management System.

These models define the core entities of the application:

* :class:`Category` – a grouping for books (e.g. Fiction, Science).
* :class:`Book` – represents a book in the catalog with a title,
  author, category and copy counts.
* :class:`Borrow` – records the borrowing of a book by a user,
  including due dates and return timestamps. It exposes helper
  properties to determine overdue status.
"""

from __future__ import annotations

from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    """Simple category for grouping books."""
    name = models.CharField(max_length=120, unique=True)

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    """Represents a book in the library's catalog."""
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="books",
        help_text="Select the category this book belongs to.",
    )
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)

    # Optional cover image for the book.  When provided, this image will be displayed
    # in the catalog and book detail pages.  Images are uploaded to the
    # ``book_covers`` directory within ``MEDIA_ROOT``.  The field is
    # marked as optional so existing records remain valid without requiring an
    # image.  When no image is uploaded, a default placeholder image is used
    # in templates via the ``static`` files system.
    cover_image = models.ImageField(
        upload_to="book_covers/", blank=True, null=True
    )

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return f"{self.title} — {self.author}"

    def can_borrow(self) -> bool:
        """Return True if there is at least one available copy."""
        return self.available_copies > 0

    @property
    def borrowed_copies(self) -> int:
        """
        Return the number of copies currently borrowed.

        This convenience property calculates the difference between the
        total number of copies and the number of copies still available.
        It is useful when adjusting ``total_copies`` to ensure the library
        does not set the total lower than the number of active loans.
        """
        return self.total_copies - self.available_copies


class Borrow(models.Model):
    """Represents a record of a user borrowing a book."""
    borrower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="borrows",
        help_text="The user who borrowed the book.",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name="borrows",
        help_text="The book that was borrowed.",
    )
    borrowed_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-borrowed_at"]

    def __str__(self) -> str:
        return f"{self.borrower.username} borrowed {self.book.title}"

    @property
    def is_returned(self) -> bool:
        """Return True if the book has been returned."""
        return self.returned_at is not None

    @property
    def is_overdue(self) -> bool:
        """Return True if the book is not returned and past its due date."""
        return (self.returned_at is None) and (timezone.now() > self.due_date)

    @classmethod
    def default_due_date(cls) -> timezone.datetime:
        """Provide a default due date 14 days from now."""
        return timezone.now() + timedelta(days=14)