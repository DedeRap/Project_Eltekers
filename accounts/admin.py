# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Menambahkan field 'level' ke form tambah/ubah pengguna
    list_display = ('username', 'email', 'nomor_telepon', 'is_staff', 'level', 'is_superuser')
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('level', 'nomor_telephon')}),
    )

    def get_fieldsets(self, request, obj=None):
        # Panggil metode asli terlebih dahulu
        fieldsets = super().get_fieldsets(request, obj)

        # Jika pengguna yang sedang login BUKAN seorang superuser
        if not request.user.is_superuser:
            # Kembalikan tata letak form yang terbatas
            return (
                (None, {'fields': ('username', 'password')}),
                ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
                # Di bagian "Permissions", hanya tampilkan 'is_active'
                ('Permissions', {'fields': ('is_active',)}),
                ('Important dates', {'fields': ('last_login', 'date_joined')}),
                # Hapus fieldset untuk 'level' dan 'nomor_telepon' jika tidak ingin staf biasa mengubahnya
            )
        
        # Jika pengguna adalah superuser, kembalikan tata letak form lengkap
        # Kita tambahkan field kustom kita di sini
        return (
            (None, {'fields': ('username', 'password')}),
            ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'nomor_telepon')}),
            ('Informasi Tambahan', {'fields': ('level',)}),
            ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
            ('Important dates', {'fields': ('last_login', 'date_joined')}),
        )

# Daftarkan CustomUser dengan CustomUserAdmin
admin.site.register(CustomUser, CustomUserAdmin)