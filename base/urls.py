# base/urls.py

from . import views
from django.urls import path, include
from .views import authView, home, logout, otp_verify, resend_otp,  CustomLoginView
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .views import PasswordResetView 

# Kita hanya mendefinisikan URL yang spesifik untuk aplikasi 'base'
urlpatterns = [

    # URL Sistem Akun (Pendaftaran, OTP, Login, Logout)
    path("signup/", authView, name="account_signup"),
    path('otp-verify/', otp_verify, name='otp_verify'),
    path("resend-otp/", views.resend_otp, name="resend_otp"),
    path("login/", CustomLoginView.as_view(), name="account_login"), # Ganti nama ke 'account_login' agar konsisten
    path("accounts/logout/", views.custom_logout, name="account_logout"), # Pastikan view logout kustom yang dipakai

    # URL Reset Password (Untuk penggunaan email, alangkah baiknya menggunakan allauth)
    #path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html', email_template_name='registration/password_reset_email.html', subject_template_name='registration/password_reset_subject.txt', success_url='/password_reset/done/'), name='password_reset'),
    #path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    #path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html', success_url = reverse_lazy('password_reset_complete')), name='password_reset_confirm'),
    #path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # URL Reset Password (Penggunaan nomor telepon)
    # Sebelum Login
    path('password-reset/', views.request_password_reset_otp, name='password_reset_request'),
    path('password-reset/verify/', views.verify_password_reset_otp, name='password_reset_otp_verify'),
    path('password-reset/set/', views.set_new_password, name='password_reset_set_new'),
    path('password-reset/resend-otp/', views.resend_password_reset_otp, name='password_reset_resend_otp'),
    path('password-reset/set-new/', views.set_new_password, name='password_reset_set_new'),
    # Setelah Login
    path('password-change/', views.CustomPasswordChangeView.as_view(template_name='account/password_change_form.html', success_url='/accounts/password-change/done/'), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='account/password_change_done.html'), name='password_change_done'),
    
]