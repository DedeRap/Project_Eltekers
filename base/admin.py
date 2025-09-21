from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from .models import Sasana

User = get_user_model()

class MyUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'nomor_telepon', 'is_staff', 'level', 'is_superuser')

    fieldsets = (
        ('Informasi Pengguna', {
            'fields': ('first_name', 'last_name', 'email', 'nomor_telepon', 'level')
        }),
        BaseUserAdmin.fieldsets[2],
        BaseUserAdmin.fieldsets[3],
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if 'groups' in form.base_fields:
            queryset = form.base_fields['groups'].queryset
            form.base_fields['groups'].queryset = queryset.exclude(name='Admin')
        return form
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            readonly_fields = list(super().get_readonly_fields(request, obj))
            return self.readonly_fields + ('is_staff', 'is_superuser')
        return self.readonly_fields
    
    def has_add_permission(self, request):
        return False
    
class SasanaAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_view_permission(self, request, obj = None):
        return False
    
class SitusAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_view_permission(self, request, obj = None):
        return False
    

    
# Daftar Tambahan
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)

# Daftar model Sasana
admin.site.register(Sasana, SasanaAdmin)

# Unregister admin default untuk Site, lalu register dengan yang kustom
admin.site.unregister(Site)
admin.site.register(Site, SitusAdmin)