from django.conf import settings
from django.contrib import admin
from django.urls import path, URLResolver

urlpatterns: list[URLResolver] = [
]

if getattr(settings, 'CARDROOM_ADMIN_URLS', False):
    urlpatterns.append(path('admin/', admin.site.urls))
