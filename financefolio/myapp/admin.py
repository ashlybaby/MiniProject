from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User

class UserAdmin(BaseUserAdmin):
    # Fields to be displayed in the admin list view
    list_display = ('email', 'first_name', 'last_name', 'is_admin', 'is_staff', 'is_active')
    list_filter = ('is_admin', 'is_staff', 'is_superuser', 'is_active')

    # Fields to be used in the form for editing a User
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'gender', 'age', 'address', 'city', 'state')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_staff', 'is_superuser')}),
        ('Important Dates', {'fields': ('date_joined', 'last_login')}),
    )

    # Fields for creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ()

# Register the custom UserAdmin
admin.site.register(User, UserAdmin)

# Optionally unregister the Group model if not used
admin.site.unregister(Group)
