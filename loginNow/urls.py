"""
URL configuration for loginNow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from base import views

handler404 = 'base.views.custom_404'
handler500 = 'base.views.custom_500'

urlpatterns = [
    # URL Khusus untuk Akun dan nyambung dengan base/urls.py
    path("XqGfinRer=1_@7791/", admin.site.urls),
    path('', views.home, name='home'),
    path('accounts/', include('base.urls')),

    # URL Profil & Pengaturan
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path("toggle-dark-mode/", views.toggle_dark_mode, name='toggle_dark_mode'),

    # URL dari Bintang
     path('sasana/', views.list_sasana, name='list-sasana'), 
    path('sasana/tambah/', views.create_sasana, name='create-sasana'),
    path('sasana/<uuid:id_sasana>/', views.detail_sasana, name='detail-sasana'),
    path('sasana/<uuid:id_sasana>/edit/', views.update_sasana, name='update-sasana'),
    path('sasana/<uuid:id_sasana>/hapus/', views.delete_sasana, name='delete-sasana'),

    path('<uuid:sasana_id>/peserta/', views.list_peserta, name='list-peserta'),
    path('<uuid:sasana_id>/peserta/tambah/', views.create_peserta, name='create-peserta'),
    path('peserta/<uuid:id_peserta>/', views.detail_peserta, name='detail-peserta'),
    path('peserta/<uuid:id_peserta>/edit/', views.update_peserta, name='update-peserta'),
    path('peserta/<uuid:id_peserta>/hapus/', views.delete_peserta, name='delete-peserta'),

    path('<uuid:sasana_id>/instruktur/', views.list_instruktur, name='list-instruktur'),
    path('<uuid:sasana_id>/instruktur/tambah/', views.create_instruktur, name='create-instruktur'),
    path('instruktur/<uuid:id_instruktur>/', views.detail_instruktur, name='detail-instruktur'),
    path('instruktur/<uuid:id_instruktur>/edit/', views.update_instruktur, name='update-instruktur'),
    path('instruktur/<uuid:id_instruktur>/hapus/', views.delete_instruktur, name='delete-instruktur'),

    # URL dari Bu Binti
    path('input/', views.input_sasana, name='input_sasana'),
    path('terdekat/', views.cari_sasana_terdekat, name='cari_sasana_terdekat'),

    # URL Lainnya
    path('lokasi/', views.lokasi_view, name='lokasi'),
    path('analisa/', views.analisa_view, name='analisa'),
    path('latihan/', views.latihan_view, name='latihan'),
    path('index/', views.index_view, name='index'),

] 


# urlpatterns += staticfiles_urlpatterns()
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Jika DEBUG False, static tidak bisa dijalankan! Oleh karena itu hapus lah "if settings.DEBUG"
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)