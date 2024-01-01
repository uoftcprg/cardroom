from django.contrib import admin
from django.urls import path, URLResolver

from cardroom.utilities import get_admin_urls

urlpatterns: list[URLResolver] = [
]

if get_admin_urls():
    urlpatterns.append(path('admin/', admin.site.urls))
