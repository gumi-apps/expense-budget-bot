from django.contrib import admin

from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "first_name", "last_name"]

    list_filter = ["date_joined"]


class IncomeAdmin(admin.ModelAdmin):
    list_display = ["reason", "amount"]
    list_filter = ["reason"]


admin.site.register(User, UserAdmin)
admin.site.register(Income, IncomeAdmin)
