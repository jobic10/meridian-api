from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class MeridianUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Meridian", {"fields": ("name", "role", "specialisation")}),
    )
    list_display = ("username", "name", "role", "is_active")
    list_filter = ("role", "is_active")
