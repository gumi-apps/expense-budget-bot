from django.contrib import admin
from django.urls import path
from bot1.views import *

urlpatterns = [
    path("/", test),
    path("admin/", admin.site.urls),
    path("/bot1", webhook),
]
