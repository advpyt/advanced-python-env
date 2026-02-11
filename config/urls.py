
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns: list = [
    path("admin/", admin.site.urls),
    # Route root URL patterns to the library application
    path("", include("library.urls")),
]

# In development mode (when ``DEBUG`` is True) we serve media files
# directly from Django.  ``MEDIA_URL`` and ``MEDIA_ROOT`` are defined in
# ``settings.py``.  In a production environment these files should be
# served by the web server or a CDN.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)