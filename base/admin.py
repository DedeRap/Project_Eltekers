from django.contrib import admin
from django.contrib.sites.models import Site
from .models import Sasana

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
    
# Daftar model Sasana
admin.site.register(Sasana, SasanaAdmin)

# Unregister admin default untuk Site, lalu register dengan yang kustom
admin.site.unregister(Site)
admin.site.register(Site, SitusAdmin)