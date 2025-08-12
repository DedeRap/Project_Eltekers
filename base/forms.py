# forms.py
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from allauth.account.forms import SignupForm
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from decouple import config
from django import forms
from django.forms import ModelForm
from .models import Profile
import bleach
from allauth.account.forms import LoginForm
# Dari Bintang:
from django import forms
from .models import Sasana, Peserta, Instruktur

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    # Definisikan field tambahan yang Anda inginkan di sini
    nomor_telepon = forms.CharField(
        max_length=15, 
        label="Nomor Telepon", 
        required=True,
        help_text="Gunakan nomor telepon yang berbeda!"
    )
    email = forms.EmailField(
        required=False, 
        label="Email (Opsional)",
        help_text="Digunakan untuk pemulihan akun."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Daftarkan semua field non-password di sini.
        # UserCreationForm akan otomatis menambahkan field password dan konfirmasi password.
        fields = ('username', 'email', 'nomor_telepon')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hapus baris print debugging jika sudah tidak diperlukan
        # print("Fields di dalam form:", self.fields.keys())

        # Atur ulang label dan placeholder sesuai keinginan Anda
        self.fields['username'].widget.attrs.update({'placeholder': 'Masukkan nama pengguna'})
        self.fields['nomor_telepon'].widget.attrs.update({'placeholder': 'Contoh: 081234567890'})
        self.fields['password1'].label = 'Kata Sandi'
        self.fields['password1'].widget.attrs.update({'placeholder': 'Minimal 8 karakter'})
        self.fields['password2'].label = 'Konfirmasi Kata Sandi'
        self.fields['password2'].widget.attrs.update({'placeholder': 'Ketik ulang kata sandi Anda'})

        # Beri class 'form-control' ke semua field agar seragam
        for fieldname in self.fields:
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})

    def clean_nomor_telepon(self):
        nomor = self.cleaned_data.get('nomor_telepon')
        if User.objects.filter(nomor_telepon=nomor).exists():
            raise forms.ValidationError("Nomor telepon ini sudah terdaftar.")
        return nomor

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email ini sudah digunakan. Mohon gunakan email lain.")
        return email

class CustomLoginForm(AuthenticationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Username atau Email'}
        )
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Kata Sandi'}
        )
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'displayname', 'info']

    def clean_image(self):
        image = self.cleaned_data.get('image', False)
        if image:
            if image.size > 3 * 1024 * 1024:
                raise forms.ValidationError("Ukuran gambar tidak boleh lebih dari 3MB!")
        return image
    
    def clean_info(self):
        info_text = self.cleaned_data.get('info', '')
        return bleach.clean(info_text, strip=True)
    
    def clean_displayname(self):
        displayname_text = self.cleaned_data.get('displayname', '')
        return bleach.clean(displayname_text, strip=True)
    
class PasswordResetRequestForm(forms.Form):
    # Pengguna bisa memasukkan username atau nomor telepon
    username_or_phone = forms.CharField(label="Username atau Nomor Telepon", max_length=150)
    
# Dari Bintang:
class SasanaForm(forms.ModelForm):
    # DEFINISIKAN FIELD LOKASI SECARA EKSPLISIT DI SINI
    # Ini memberitahu Django untuk menerima teks biasa, bukan memvalidasi pilihan.
    provinsi = forms.CharField(
        label='Provinsi',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    kota_kabupaten = forms.CharField(
        label='Kota/Kabupaten',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    kecamatan = forms.CharField(
        label='Kecamatan',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    kelurahan = forms.CharField(
        label='Kelurahan',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Sasana
        fields = [
            'nama_sasana', 'sejak', 'alamat_sasana',
            'provinsi', 'kota_kabupaten', 'kecamatan', 'kelurahan',
            'jumlah_instruktur', 'jumlah_peserta', 'peserta_aktif',
            'jumlah_latihan_per_minggu', 'link_gmap', 'profile'
        ]
        
        widgets = {
            'nama_sasana': forms.TextInput(attrs={'class': 'form-control'}),
            #'pengurus': forms.Select(attrs={'class': 'form-select'}),
            'sejak': forms.NumberInput(attrs={'class': 'form-control'}),
            'alamat_sasana': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'jumlah_instruktur': forms.NumberInput(attrs={'class': 'form-control'}),
            'jumlah_peserta': forms.NumberInput(attrs={'class': 'form-control'}),
            'peserta_aktif': forms.NumberInput(attrs={'class': 'form-control'}),
            'jumlah_latihan_per_minggu': forms.NumberInput(attrs={'class': 'form-control'}),
            'link_gmap': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://maps.app.goo.gl/abcdefg12345'}),
            'profile': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    #def __init__(self, *args, **kwargs):
    #    super().__init__(*args, **kwargs)

    #    pengurus_field = self.fields['pengurus']

    #    pengurus_field.label = "Pilih Pengurus Sasana"

    #    pengurus_field.queryset = User.objects.filter(level=3)

    #    if not self.instance.pk:
    #        existing_pengurus_ids = Sasana.objects.values_list('pengurus_id', flat=True)
    #        pengurus_field.queryset = pengurus_field.queryset.exclude(id__in=existing_pengurus_ids)

    #    pengurus_field.label_from_instance = lambda obj: f"{obj.username} ({obj.email or 'Tidak ada Email'})"


class PesertaForm(forms.ModelForm):
    class Meta:
        model = Peserta
        fields = '__all__'
        widgets = {
            'nama_peserta': forms.TextInput(attrs={'class': 'form-control'}),
            'tanggal_lahir_peserta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'kendala_terapi': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sasana': forms.Select(attrs={'class': 'form-control'}),
        }

class InstrukturForm(forms.ModelForm):
    class Meta:
        model = Instruktur
        fields = '__all__'
        widgets = {
            'nama_instruktur': forms.TextInput(attrs={'class': 'form-control'}),
            'sertifikasi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tanggal_sertifikasi': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'file_sertifikat': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'sasana': forms.Select(attrs={'class': 'form-control'}),
        }