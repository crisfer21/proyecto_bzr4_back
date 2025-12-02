from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Mostrar el campo rol en la lista de usuarios
    list_display = ("username", "email", "role", "is_staff", "is_active")

    # Permitir búsqueda por rol
    search_fields = ("username", "email", "role")

    # Añadir rol a los fieldsets de edición
    fieldsets = UserAdmin.fieldsets + (
        ("Información adicional", {"fields": ("role",)}),
    )

    # Añadir rol al formulario de creación
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Información adicional", {"fields": ("role",)}),
    )
