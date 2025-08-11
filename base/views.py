import random
import requests
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from base.forms import CustomUserCreationForm # Dari base itu sendiri!
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import auth
from django.contrib.auth import logout
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.contrib.auth.forms import ( AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm)
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.views import PasswordContextMixin
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.tokens import default_token_generator
from django.utils.decorators import method_decorator
#from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseForbidden
from allauth.account.utils import send_email_confirmation
from django.contrib.auth.views import redirect_to_login
from .forms import *
from django.db.models import Q
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
from django.shortcuts import resolve_url
from django.contrib.auth import get_user_model
from .forms import ProfileForm
from .forms import CustomLoginForm
from .forms import CustomUserCreationForm # Pastikan path import ini benar
#Dari Bintang:
from .forms import SasanaForm, PesertaForm, InstrukturForm
from .models import Sasana, Instruktur, Peserta
#Dari bang Anka:
import os
from django.core.files.storage import FileSystemStorage
# Dari Bu Binti
from math import radians, cos, sin, asin, sqrt
from django.http import JsonResponse
import re

User = get_user_model()
class CustomAccountAdapter(DefaultAccountAdapter):
    def get_signup_redirect_url(self, request):
        return resolve_url("otp_verify") 
    
    
class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get("email")
        
        if not email:
            return
        
        if not sociallogin.is_existing:
            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                sociallogin.connect(request, existing_user)
        
        if sociallogin.is_existing: 
            user = sociallogin.user
            email_address, created = EmailAddress.objects.get_or_create(user=user, email=email)
            if not email_address.verified:
                email_address.verified = True
                email_address.save()
                
                
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        email = user.email
        email_address, created = EmailAddress.objects.get_or_create(user=user, email=email)
        if not email_address.verified:
            email_address.verified = True
            email_address.save()
            
        return user

class CustomLoginView(LoginView):
    """
    View login ini sekarang menggunakan form kustom yang sudah
    menangani validasi reCAPTCHA secara otomatis.
    """
    template_name = 'account/login.html'
    form_class = CustomLoginForm  # <-- INI BAGIAN KUNCINYA!  

def kirim_otp_via_sms(nomor_telepon, otp):
    # Di sinilah Anda akan menempatkan kode untuk memanggil API gateway SMS/WA
    # Contoh:
    # endpoint = "https://api.provider.com/send"
    # payload = {'to': nomor_telepon, 'message': f'Kode OTP Anda: {otp}'}
    # headers = {'Authorization': 'Bearer YOUR_API_KEY'}
    # requests.post(endpoint, json=payload, headers=headers)
    print("========================================")
    print(f"SIMULASI MENGIRIM OTP KE: {nomor_telepon}")
    print(f"KODE OTP: {otp}")
    print("========================================")

def request_password_reset_otp(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            username_or_phone = form.cleaned_data['username_or_phone']
            try:
                # Cari user berdasarkan username ATAU nomor telepon
                user = User.objects.get(Q(username=username_or_phone) | Q(nomor_telepon=username_or_phone))
                
                # Buat OTP
                otp = str(random.randint(100000, 999999))
                
                # Simpan informasi di session
                request.session['reset_otp'] = otp
                request.session['reset_otp_user_id'] = user.id
                # Tambahkan waktu kedaluwarsa jika perlu
                
                # Kirim OTP
                kirim_otp_via_sms(user.nomor_telepon, otp)
                
                messages.success(request, 'Kode OTP telah dikirim ke nomor telepon Anda.')
                return redirect('password_reset_otp_verify') # Arahkan ke halaman verifikasi OTP

            except User.DoesNotExist:
                messages.error(request, 'Pengguna dengan username atau nomor telepon tersebut tidak ditemukan.')

    else:
        form = PasswordResetRequestForm()
        
    return render(request, 'account/password_reset_request_form.html', {'form': form})

def verify_password_reset_otp(request):
    if 'reset_otp_user_id' not in request.session:
        messages.error(request, 'Sesi tidak valid. Mohon ulangi permintaan reset password.')
        return redirect('password_reset_request')

    if request.method == 'POST':
        input_otp = request.POST.get('otp')
        if input_otp == request.session.get('reset_otp'):
            # OTP Benar, tandai sesi sebagai terverifikasi
            request.session['reset_otp_verified'] = True
            messages.success(request, 'OTP benar. Silakan atur password baru Anda.')
            return redirect('password_reset_set_new') # Arahkan ke halaman set password baru
        else:
            messages.error(request, 'Kode OTP salah.')
            
    return render(request, 'account/password_reset_otp_verify.html')

def set_new_password(request):
    if not request.session.get('reset_otp_verified'):
        messages.error(request, 'Akses tidak sah. Mohon verifikasi OTP terlebih dahulu.')
        return redirect('password_reset_request')

    user_id = request.session.get('reset_otp_user_id')
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            # Hapus semua data session setelah berhasil
            for key in list(request.session.keys()):
                if key.startswith('reset_otp'):
                    del request.session[key]
            messages.success(request, 'Password Anda telah berhasil diubah. Silakan masuk.')
            return redirect('account_login')
    else:
        form = SetPasswordForm(user)

    return render(request, 'account/password_reset_set_new.html', {'form': form})


@login_required
@never_cache
def home(request):
    return render(request, "home.html", {})

class CustomPasswordChangeView(PasswordChangeView):
    def post(self, request, *args, **kwargs):
        # Ambil token reCAPTCHA dari form
        recaptcha_token = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_V3_SECRET_KEY,
            'response': recaptcha_token
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        print(f"RECAPTCHA V3 RESULT: {result}") #Tampilkan hasil score(Hapus ini jika tidak mode DEBUG!)

        # Periksa apakah reCAPTCHA valid dan skornya mencukupi
        if result.get('success') and result.get('score', 0) >= 0.5:
            # Jika lolos, lanjutkan ke proses normal dari parent view
            return super().post(request, *args, **kwargs)
        else:
            # Jika gagal, tampilkan pesan error dan render kembali form
            messages.error(request, 'Verifikasi reCAPTCHA gagal, terdeteksi aktivitas mencurigakan.')
            # Panggil self.get_form() untuk mendapatkan instance form yang akan dirender
            form = self.get_form()
            return self.render_to_response(self.get_context_data(form=form))

    # Kirim site key ke template agar bisa digunakan oleh JavaScript
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['RECAPTCHA_V3_SITE_KEY'] = settings.RECAPTCHA_V3_SITE_KEY
        return context
    

@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # ================== AWAL MODIFIKASI reCAPTCHA v3 ==================
        recaptcha_token = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_V3_SECRET_KEY,
            'response': recaptcha_token
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        print(f"RECAPTCHA V3 RESULT: {result}") #Tampilkan hasil score(Hapus ini jika tidak mode DEBUG!)

        if result.get('success') and result.get('score', 0) >= 0.4:
            # Jika reCAPTCHA valid dan skor bagus, lanjutkan proses form
            form = ProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profil Anda telah berhasil diperbarui!')
                return redirect('home')
        else:
            # Jika reCAPTCHA gagal atau skor terlalu rendah
            messages.error(request, 'Gagal menyimpan, terdeteksi aktivitas mencurigakan.')
            # Inisialisasi kembali form dengan data yang ada agar tidak hilang
            form = ProfileForm(request.POST, instance=profile)
            context = {
                'form': form,
                'site_key_v3': settings.RECAPTCHA_V3_SITE_KEY
            }
            return render(request, 'profile_edit.html', context)
        # ================== AKHIR MODIFIKASI reCAPTCHA v3 ==================

    # Bagian ini tidak berubah, dieksekusi saat method GET
    form = ProfileForm(instance=profile)
    context = {
        'form': form,
        'site_key_v3': settings.RECAPTCHA_V3_SITE_KEY  # <-- TAMBAHKAN INI
    }
    return render(request, 'profile_edit.html', context)

# di dalam base/views.py

# ... (import Anda yang lain) ...
# Pastikan EmailAddress juga diimpor
from allauth.account.models import EmailAddress

@never_cache
@require_http_methods(["GET", "POST"])
def authView(request):
    # Logika untuk method POST
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)

        recaptcha_token = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_V3_SECRET_KEY,
            'response': recaptcha_token
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        print(f"RECAPTCHA V3 RESULT: {result}") #Tampilkan hasil score(Hapus ini jika tidak mode DEBUG!)

        # 3. Cek hasil reCAPTCHA
        if result.get('success') and result.get('score', 0) >= 0.5:
            print(f"RECAPTCHA V3 RESULT: {result}") #Tampilkan hasil score(Hapus ini jika tidak mode DEBUG!)
            # 4. Jika reCAPTCHA lolos, baru validasi formnya
            if form.is_valid():
                # Jika form valid, lanjutkan logika OTP dan redirect
                #user = form.save(commit=False)
                #user.is_active = False
                #user.save()

                request.session['registration_data'] = {
                    'nomor_telepon': form.cleaned_data.get('nomor_telepon'),
                    'username': form.cleaned_data.get('username'),
                    'password': form.cleaned_data.get('password2'),
                    'email': form.cleaned_data.get('email', '') 
                }

                otp = str(random.randint(100000, 999999))
                #email = form.cleaned_data.get('email')
                #request.session['otp_user_id'] = user.id
                request.session['otp'] = otp
                request.session['otp_created_time'] = timezone.now().isoformat()
                request.session['otp_attempts'] = 0

                nomor_telepon = form.cleaned_data.get('nomor_telepon')
                #send_mail('Kode OTP dari Eltekers', f'Kode OTP Verifikasi anda adalah: {otp}', 'dederadeaajiprasojo@gmail.com', [email], fail_silently=False)
                #messages.success(request, f"Kode OTP telah dikirim ke {email}. Mohon periksa email Anda.")
                #return redirect("otp_verify")

                print("========================================")
                print(f"SIMULASI MENGIRIM OTP KE: {nomor_telepon}")
                print(f"KODE OTP: {otp}")
                print("========================================")

                messages.success(request, f"Kode OTP telah dikirim (cek terminal Anda).")
                return redirect("otp_verify")
            else:
                print(f"RECAPTCHA V3 RESULT: {result}") #Tampilkan hasil score(Hapus ini jika tidak mode DEBUG!)
        else:
            # Jika reCAPTCHA gagal, tambahkan pesan error.
            messages.error(request, 'Gagal memverifikasi reCAPTCHA. Aktivitas Anda mencurigakan.')
            # Kode juga akan lanjut ke bawah untuk me-render ulang halaman
            # dengan data yang sudah diisi pengguna.

    # Logika untuk method GET
    else:
        # Jika ini adalah kunjungan pertama (GET), buat form kosong
        form = CustomUserCreationForm()

    # Ini adalah "Catch-all Render" di akhir fungsi.
    # Ini akan dieksekusi untuk SEMUA kasus yang perlu menampilkan halaman.
    context = {
        'form': form,
        'site_key_v3': settings.RECAPTCHA_V3_SITE_KEY
        }
    return render(request, "account/signup.html", context)


@never_cache
def otp_verify(request):
    otp_time_str = request.session.get("otp_created_time")
    reg_data = request.session.get('registration_data')
    #user_id = request.session.get("otp_user_id")
    
    if not otp_time_str or not reg_data:
        messages.error(request, "Sesi tidak valid. Mohon lakukan pendaftaran ulang.")
        return redirect('account_signup')
    
    otp_time = timezone.datetime.fromisoformat(otp_time_str)
    expiry_time = otp_time + timedelta(minutes=5)
    expiry_timestamp = int(expiry_time.timestamp() * 1000)

    if request.method == "POST":
        recaptcha_token = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_V3_SECRET_KEY,
            'response': recaptcha_token
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        print(f"RECAPTCHA V3 RESULT: {result}") #Tampilkan hasil score(Hapus ini jika tidak mode DEBUG!)

        if not (result.get('success') and result.get('score', 0) >= 0.5):
            messages.error(request, "Verifikasi reCAPTCHA gagal, aktivitas Anda mencurigakan.")

        else:
            # Cek apakah OTP sudah kadaluarsa (cek lagi di dalam POST untuk keamanan)
            if timezone.now() > expiry_time:
                request.session.flush()
                messages.error(request, "OTP sudah kadaluarsa. Mohon lakukan pendaftaran ulang.")
                return redirect('account_signup')
                
            input_code = request.POST.get("otp")
            otp_code = request.session.get("otp")
            
            if input_code == otp_code:
                try:
                    user = User.objects.create_user(username=reg_data['username'], email=reg_data.get('email'), password=reg_data['password'], nomor_telepon=reg_data.get('nomor_telepon'))
                    if reg_data.get('email'):
                        EmailAddress.objects.create(user=user, email=reg_data['email'], primary=True, verified=True)
                        
                    request.session.flush()
                    messages.success(request, "Verifikasi berhasil! Akun Anda telah dibuat. Silakan login.")
                    return redirect("account_login")
                    
                except Exception as e:
                    messages.error(request, f"Gagal membuat akun: {e}")
                    return redirect('account_signup')
                    
            else:
                # Logika jika OTP salah
                attempts = request.session.get('otp_attempts', 0) + 1
                request.session['otp_attempts'] = attempts

                if attempts >= 5:
                    request.session.flush()
                    messages.error(request, "Terlalu banyak percobaan OTP yang salah. Pendaftaran dibatalkan.")
                    return redirect('account_signup')
                    
                remaining_attempts = 5 - attempts
                messages.error(request, f"Kode OTP salah! Anda memiliki {remaining_attempts} percobaan lagi.")
            
    context = {
        "otp_expiry_timestamp": expiry_timestamp,
        "site_key_v3": settings.RECAPTCHA_V3_SITE_KEY # <-- Kunci selalu dikirim ke template
    }
    return render(request, "account/otp_verify.html", { "otp_expiry_timestamp": expiry_timestamp })

def resend_otp(request):
    #user_id = request.session.get("otp_user_id")
    reg_data = request.session.get("registration_data")
    if not reg_data:
        messages.error(request, "Sesi tidak valid untuk mengirim ulang OTP.")
        return redirect("account_signup")

    nomor_telepon = reg_data.get('nomor_telepon')
    if not nomor_telepon:
        messages.error(request, "Nomor telepon tidak ditemukan di sesi. Mohon daftar ulang.")
        return redirect("account_signup")

    otp = str(random.randint(100000, 999999))
    request.session['otp'] = otp
    request.session['otp_created_time'] = timezone.now().isoformat()
    request.session['otp_attempts'] = 0 # Reset percobaan

    #send_mail(
    #    'Kode OTP Baru Anda',
    #    f'Kode verifikasi baru Anda adalah: {otp}',
    #    'dederadeaajiprasojo@gmail.com',
    #    [user.email], # Ambil email dari objek user
    #    fail_silently=False,
    #)

    print("========================================")
    print(f"SIMULASI MENGIRIM ULANG OTP KE: {nomor_telepon}")
    print(f"KODE OTP BARU: {otp}")
    print("========================================")

    messages.success(request, "OTP telah dikirim ulang ke email Anda.")
    return redirect("otp_verify")

@login_required
def toggle_dark_mode(request):
    # Status mode gelap saat ini
    is_dark_mode = request.session.get('dark_mode', False)

    # Balikkan nilainya (True jadi False, False jadi True)
    is_dark_mode = not is_dark_mode
    request.session['dark_mode'] = is_dark_mode

    # Atur pesan berdasarkan status yang baru
    if is_dark_mode:
        messages.success(request, 'Mode Gelap telah diaktifkan!')
    else:
        messages.success(request, 'Mode Terang telah diaktifkan!')

    return redirect('home')

def custom_logout(request):
    auth.logout(request)
    response = redirect('account_login')  
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)


#Level user:
#PERINGATAN!!! Jangan buat >= harus == jika dilakukan secara produksi.
#Jika ini tidak segera ditangani, akan terjadinya broken access controll(OWASP A01:2021)
def level_peserta(user):
    return user.is_authenticated and user.level == 1

def level_instruktur(user):
    return user.is_authenticated and user.level == 2

def level_pengurus_sasana(user):
    return user.is_authenticated and user.level == 3

def level_pengurus_daerah(user):
    return user.is_authenticated and user.level == 4

def level_pengurus_daerah_dan_instruktur(user):
    return user.is_authenticated and user.level in [2, 4]

def level_pengurus_daerah_dan_sasana(user):
    return user.is_authenticated and user.level in [3, 4]

def level_pengurus_daerah_sasana_dan_instruktur(user):
    return user.is_authenticated and user.level in [2, 3, 4]


# Dari Bintang:
# Sasana
@user_passes_test(level_pengurus_daerah)
@login_required
def create_sasana(request):
    if request.method == 'POST':
        form = SasanaForm(request.POST, request.FILES)

        recaptcha_token = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_V3_SECRET_KEY,
            'response': recaptcha_token
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        print(f"RECAPTCHA V3 RESULT: {result}") # Untuk DEBUG

        if result.get('success') and result.get('score', 0) >= 0.4:
            if form.is_valid():
                form.save()
                messages.success(request, 'Sasana berhasil ditambahkan!')
                return redirect('list-sasana')
        else:
            messages.error(request, 'Gagal menyimpan, terdeteksi adanya aktivitas mencurigakan.')
            
    else:
        form = SasanaForm()

    context = {
        'form': form,
        'site_key_v3': settings.RECAPTCHA_V3_SITE_KEY
        }
    return render(request, 'sasana_form.html', context)

# List Sasana
@user_passes_test(level_pengurus_daerah)
@login_required
def list_sasana(request):
    data = Sasana.objects.all()
    return render(request, 'sasana_list.html', {'data': data})

# Detail Sasana
@user_passes_test(level_pengurus_daerah)
@login_required
def detail_sasana(request, id_sasana):
    sasana = get_object_or_404(Sasana, id_sasana=id_sasana)
    return render(request, 'sasana_detail.html', {'sasana': sasana})

# Profil Sasana
@login_required
@user_passes_test(level_pengurus_sasana)
def my_sasana_profile(request):
    # Buat dictionary kosong untuk menampung konteks
    context = {}
    try:
        # Cari sasana, jika ketemu, masukkan ke dalam context
        sasana = Sasana.objects.get(pengurus=request.user)
        context['sasana'] = sasana
    except Sasana.DoesNotExist:
        # Jika TIDAK KETEMU, masukkan pesan error ke dalam context
        context['pesan_error'] = "Maaf, akun Anda belum terdaftar di sasana manapun. Silakan lapor kepada Pengurus Daerah untuk mengelola data sasana anda."
        # Pastikan 'sasana' tidak ada di context atau nilainya None
        context['sasana'] = None
    
    # Render template dengan context yang sudah disiapkan
    return render(request, 'profile_sasana.html', context)

# Edit Sasana
@user_passes_test(level_pengurus_sasana)
@login_required
def update_sasana(request, id_sasana):
    sasana = get_object_or_404(Sasana, id_sasana=id_sasana, pengurus=request.user)

    if request.method == 'POST':
        form = SasanaForm(request.POST, request.FILES, instance=sasana)

        recaptcha_token = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_V3_SECRET_KEY,
            'response': recaptcha_token
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        print(f"RECAPTCHA V3 RESULT: {result}") # Untuk DEBUG

        if result.get('success') and result.get('score', 0) >= 0.4:
            if form.is_valid():
                form.save()
                messages.success(request, 'Data sasana berhasil diubah!')
                return redirect('my-sasana-profile')
        else:
            messages.error(request, 'Gagal menyimpan, terdeteksi adanya aktivitas mencurigakan.')
            
    else:
        form = SasanaForm(instance=sasana)

    context = {
        'form': form,
        'site_key_v3': settings.RECAPTCHA_V3_SITE_KEY 
    }
    return render(request, 'sasana_form.html', context)

# Delete Sasana
@user_passes_test(level_pengurus_sasana)
@login_required
def delete_sasana(request, id_sasana):
    sasana = get_object_or_404(Sasana, id_sasana=id_sasana, pengurus=request.user)
    if request.method == 'POST':
        sasana.delete()
        messages.success(request, 'Data sasana telah berhasil dihapus.')
        return redirect('home')
    return render(request, 'sasana_confirm_delete.html', {'sasana': sasana})


# Peserta
@user_passes_test(level_pengurus_sasana)
@login_required
def create_peserta(request, sasana_id):
    # Logika untuk method POST
    sasana = get_object_or_404(Sasana, id_sasana=sasana_id)

    if request.method == 'POST':
        # 1. Buat instance form dengan data dari request POST
        form = PesertaForm(request.POST)
        
        # 2. Pindahkan verifikasi reCAPTCHA ke DALAM blok POST
        recaptcha_token = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_V3_SECRET_KEY,
            'response': recaptcha_token
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        print(f"RECAPTCHA V3 RESULT: {result}") # Untuk DEBUG

        # 3. Cek hasil reCAPTCHA
        if result.get('success') and result.get('score', 0) >= 0.4:
            # 4. Jika reCAPTCHA lolos, baru validasi formnya
            if form.is_valid():
                peserta = form.save(commit=False)
                peserta.sasana = sasana
                peserta.save()
                messages.success(request, 'Peserta berhasil ditambahkan!')
                return redirect('list-peserta', sasana_id=sasana.id_sasana) # atau ke halaman daftar peserta
            # Jika form tidak valid, kode akan lanjut ke bawah untuk me-render
            # halaman lagi dengan pesan error dari form.
        else:
            # Jika reCAPTCHA gagal, tambahkan pesan error.
            messages.error(request, 'Gagal menyimpan, terdeteksi aktivitas mencurigakan.')
            # Kode juga akan lanjut ke bawah untuk me-render ulang halaman.

    # Logika untuk method GET
    else:
        # Buat form kosong, tapi bisa diisi data awal jika ada
        form = PesertaForm()
        #initial_data = {}
        #sasana_id = request.GET.get('sasana_id')
        #if sasana_id:
        #    try:
        #        sasana = Sasana.objects.get(id_sasana=sasana_id)
        #        initial_data['sasana'] = sasana
        #    except Sasana.DoesNotExist:
        #        pass
        #form = PesertaForm(initial=initial_data)

    # Titik render tunggal yang menangani GET dan semua kasus GAGAL pada POST
    context = {
        'form': form, 'sasana': sasana,
        'site_key_v3': settings.RECAPTCHA_V3_SITE_KEY # <-- Kunci selalu dikirim
        }
    return render(request, 'peserta_form.html', context)

# List Peserta
@user_passes_test(level_pengurus_daerah_sasana_dan_instruktur)
@login_required
def list_peserta(request, sasana_id):
    sasana = get_object_or_404(Sasana, id_sasana=sasana_id)
    data = Peserta.objects.filter(sasana=sasana)
    return render(request, 'peserta_list.html', {'data': data, 'sasana': sasana})

# Detail Peserta
@user_passes_test(level_pengurus_daerah_sasana_dan_instruktur)
@login_required
def detail_peserta(request, id_peserta):
    peserta = get_object_or_404(Peserta, id_peserta=id_peserta)
    return render(request, 'peserta_detail.html', {'peserta': peserta})

# Edit Peserta
@user_passes_test(level_pengurus_sasana)
@login_required
def update_peserta(request, id_peserta):
    peserta = get_object_or_404(Peserta, id_peserta=id_peserta)
    sasana = peserta.sasana

    if request.method == 'POST':
        form = PesertaForm(request.POST, instance=peserta)

        recaptcha_token = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_V3_SECRET_KEY,
            'response': recaptcha_token
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        print(f"RECAPTCHA V3 RESULT: {result}") # Untuk DEBUG

        if result.get('success') and result.get('score', 0) >= 0.4:
            if form.is_valid():
                form.save()
                messages.success(request, 'Data peserta berhasil diedit!')
                return redirect('list-peserta', sasana_id=sasana.id_sasana)
        else:
            messages.error(request, 'Gagal menyimpan, terdeteksi adanya aktivitas mencurigakan.')
    else:
        form = PesertaForm(instance=peserta)

    context = {
        'form': form, 'sasana': sasana, 'peserta': peserta,
        'site_key_v3': settings.RECAPTCHA_V3_SITE_KEY # <-- Kunci selalu dikirim
        }
    return render(request, 'peserta_form.html', context)

# Delete Peserta
@user_passes_test(level_pengurus_sasana)
@login_required
def delete_peserta(request, id_peserta):
    peserta = get_object_or_404(Peserta, id_peserta=id_peserta)
    sasana_untuk_redirect = peserta.sasana.id_sasana
    if request.method == 'POST':
        peserta.delete()
        return redirect('list-peserta', sasana_id=sasana_untuk_redirect)
    return render(request, 'peserta_confirm_delete.html', {'peserta': peserta})


# Instruktur
@user_passes_test(level_pengurus_sasana)
@login_required
def create_instruktur(request, sasana_id):
    sasana = get_object_or_404(Sasana, id_sasana=sasana_id)

    if request.method == 'POST':
        form = InstrukturForm(request.POST, request.FILES)

        recaptcha_token = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_V3_SECRET_KEY,
            'response': recaptcha_token
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        print(f"RECAPTCHA V3 RESULT: {result}") # Untuk DEBUG

        if result.get('success') and result.get('score', 0) >= 0.4:
            if form.is_valid():
                instruktur = form.save(commit=False)
                instruktur.sasana = sasana
                instruktur.save()
                messages.success(request, 'Data instruktur berhasil ditambahkan!')
                return redirect('list-instruktur', sasana_id=sasana.id_sasana)
        else:
            messages.error(request, 'Gagal menyimpan, terdeteksi adanya aktivitas mencurigakan.')

    else:
        form = InstrukturForm()
        #initial_data = {}
        #sasana_id = request.GET.get('sasana_id')
        #if sasana_id:
        #    try:
        #        sasana = Sasana.objects.get(id_sasana=sasana_id)
        #        initial_data['sasana'] = sasana
        #    except Sasana.DoesNotExist:
        #        pass
        #form = InstrukturForm(initial=initial_data)

    context = {
        'form': form, 'sasana': sasana,
        'site_key_v3': settings.RECAPTCHA_V3_SITE_KEY
    }
    return render(request, 'instruktur_form.html', context)

# List Instruktur
@user_passes_test(level_pengurus_daerah_dan_sasana)
@login_required
def list_instruktur(request, sasana_id):
    sasana = get_object_or_404(Sasana, id_sasana=sasana_id)
    data = Instruktur.objects.filter(sasana=sasana)
    return render(request, 'instruktur_list.html', {'data': data, 'sasana': sasana})

# Detail Instruktur
@user_passes_test(level_pengurus_daerah_dan_sasana)
@login_required
def detail_instruktur(request, id_instruktur):
    instruktur = get_object_or_404(Instruktur, id_instruktur=id_instruktur)
    return render(request, 'instruktur_detail.html', {'instruktur': instruktur})

# Update Instruktur
@user_passes_test(level_pengurus_sasana)
@login_required
def update_instruktur(request, id_instruktur):
    instruktur = get_object_or_404(Instruktur, id_instruktur=id_instruktur)
    sasana = instruktur.sasana

    if request.method == 'POST':
        form = InstrukturForm(request.POST, request.FILES, instance=instruktur)

        recaptcha_token = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_V3_SECRET_KEY,
            'response': recaptcha_token
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        print(f"RECAPTCHA V3 RESULT: {result}") # Untuk DEBUG

        if result.get('success') and result.get('score', 0) >= 0.4:
            if form.is_valid():
                form.save()
                messages.success(request, 'Data instruktur berhasil diubah!')
                return redirect('list-instruktur', sasana_id=sasana.id_sasana)
        else:
            messages.error(request, 'Gagal menyimpan, terdeteksi adanya aktivitas mencurigakan.')

    else:
        form = InstrukturForm(instance=instruktur)

    context = {
        'form': form, 'sasana': sasana, 'instrutur': instruktur,
        'site_key_v3': settings.RECAPTCHA_V3_SITE_KEY
        }
    return render(request, 'instruktur_form.html', context)

# Delete Instruktur
@user_passes_test(level_pengurus_sasana)
@login_required
def delete_instruktur(request, id_instruktur):
    instruktur = get_object_or_404(Instruktur, id_instruktur=id_instruktur)
    sasana_untuk_redirect = instruktur.sasana.id_sasana

    if request.method == 'POST':
        instruktur.delete()
        return redirect('list-instruktur', sasana_id=sasana_untuk_redirect)
    return render(request, 'instruktur_confirm_delete.html', {'instruktur': instruktur})

# Untuk Reza
def index_view(request):
    return render(request, 'widgets/index.html')

def latihan_view(request):
    return render(request, 'widgets/latihan.html')

def lokasi_view(request):
    return render(request, 'widgets/lokasi.html')


@login_required
@never_cache
def pengaturan_view(request):
    return render(request, 'widgets/pengaturan.html')

#Untuk bang Anka, templates dari Reza:

@login_required
@user_passes_test(lambda u: u.level >= 2) # Pastikan hanya level yang sesuai bisa akses
def analisa_view(request):
    if request.method == 'POST':
        if 'video_file' not in request.FILES:
            return render(request, 'video_processor/analisa.html', {'error_message': 'Tidak ada file video yang dipilih.'})
        
        uploaded_file = request.FILES['video_file']
        
        try:
            # Menggunakan URL dari settings.py
            submit_url = f"{settings.MIDDLEWARE_URL}/submit_video/"
            
            files = {'video_file': (uploaded_file.name, uploaded_file.read(), uploaded_file.content_type)}

            # Kirim request ke API middleware
            response = requests.post(submit_url, files=files, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            job_id = data.get('job_id')

            if not job_id:
                 return render(request, 'video_processor/analisa.html', {'error_message': 'Gagal mendapatkan Job ID dari middleware.'})

            # Arahkan ke halaman tunggu dengan job_id
            return render(request, 'video_processor/result.html', {'job_id': job_id})

        except requests.exceptions.RequestException as e:
            error_message = f"Gagal terhubung ke layanan pemrosesan video. Silakan coba lagi nanti. Error: {e}"
            return render(request, 'video_processor/analisa.html', {'error_message': error_message})
        except Exception as e:
            return render(request, 'video_processor/analisa.html', {'error_message': f"Terjadi kesalahan: {e}"})

    # Jika method GET, tampilkan halaman upload
    return render(request, 'video_processor/analisa.html')


@login_required
def check_status_view(request, job_id):
    """
    View ini dipanggil oleh JavaScript untuk memeriksa status job.
    """
    try:
        status_url = f"{settings.MIDDLEWARE_URL}/get_result/{job_id}"
        response = requests.get(status_url, timeout=10)
        response.raise_for_status()
        
        if response.headers.get('content-type') == 'video/mp4':
            fs = FileSystemStorage()
            output_filename = f"annotated_{job_id}.mp4"
            # Pastikan direktori media ada
            if not os.path.exists(settings.MEDIA_ROOT):
                os.makedirs(settings.MEDIA_ROOT)
            
            with open(os.path.join(settings.MEDIA_ROOT, output_filename), 'wb') as f:
                f.write(response.content)
            
            video_url = fs.url(output_filename)
            return JsonResponse({'status': 'completed', 'video_url': video_url})
        
        return JsonResponse(response.json())

    except requests.exceptions.RequestException:
        return JsonResponse({'status': 'failed', 'error': 'Gagal menghubungi middleware.'}, status=500)
    except Exception as e:
        return JsonResponse({'status': 'failed', 'error': str(e)}, status=500)
    
# Dari Bu Binti:
def input_sasana(request):
    if request.method == 'POST':
        form = SasanaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('input_sasana')  # bisa redirect ke halaman sukses juga
    else:
        form = SasanaForm()
    
    return render(request, 'input_sasana.html', {'form': form})

def haversine(lat1, lon1, lat2, lon2):
    # Konversi ke radian
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    # Rumus Haversine
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371  # Radius Bumi (km)
    return c * r

def extract_lat_lon(link):
    match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', link)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

def cari_sasana_terdekat(request):
    if request.method == 'POST':
        lat = float(request.POST.get('latitude'))
        lon = float(request.POST.get('longitude'))

        semua_sasana = Sasana.objects.all()
        hasil = []

        for s in semua_sasana:
            sasana_lat, sasana_lon = extract_lat_lon(s.link_gmap)
            if sasana_lat is not None and sasana_lon is not None:
                jarak = haversine(lat, lon, sasana_lat, sasana_lon)
                hasil.append({
                    'nama': s.nama_sasana,
                    'alamat': s.alamat_sasana,
                    'jarak': round(jarak, 2),
                    'link_gmap': s.link_gmap,
                    'gambar': s.profile.url if s.profile else '',
                })

        hasil = sorted(hasil, key=lambda x: x['jarak'])[:4]
        return JsonResponse({'data': hasil})

    return render(request, 'cari_sasana.html')