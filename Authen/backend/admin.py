from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User, Organisation

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser')
    fieldsets = (
            (None, {'fields': ('email', 'password')}),
            ('Personal info', {'fields': ('first_name', 'last_name', 'phone')}),
            ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
            (None, {
                'classes': ('wide',),
                'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
            }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ()


class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


admin.site.register(User, UserAdmin)
admin.site.register(Organisation, OrganisationAdmin)
admin.site.unregister(Group)
