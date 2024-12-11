from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'gender', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'gender')
    ordering = ('email',)
    search_fields = ('email', 'first_name', 'last_name')

    # Fields to display in the admin add/edit forms
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'gender', 'phone_number', 'image')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'gender', 'phone_number', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )


admin.site.register(User, CustomUserAdmin)
