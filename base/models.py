from django.db import models
from django.db.models.signals import post_delete
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.conf import settings
from django.core.validators import FileExtensionValidator
import uuid

# Create your models here.
class Event(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events', default=1)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='avatars/', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    displayname = models.CharField(max_length=20, null=True, blank=True)
    info = models.TextField(null=True, blank=True) 
    
    def __str__(self):
        return str(self.user)
    
    @property
    def name(self):
        if self.displayname:
            return self.displayname
        return self.user.username 
    
    @property
    def avatar(self):
        if self.image:
            return self.image.url
        return f'{settings.STATIC_URL}images/avatar.svg'


#Dari Bintang:
class OrganisasiDaerah(models.Model):
    id_organisasi_daerah = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

class PengurusDaerah(models.Model):
    id_pengurus_daerah = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama_pengurus_daerah = models.CharField(max_length=255)
    jabatan = models.CharField(max_length=255)
#    organisasi_daerah = models.ForeignKey(OrganisasiDaerah, on_delete=models.CASCADE)

class Sasana(models.Model):
    id_sasana = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama_sasana = models.CharField(max_length=255)
    #pengurus = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'level': 3}, verbose_name="Pengurus Sasana")
    sejak = models.IntegerField()
    alamat_sasana = models.TextField()
    provinsi = models.CharField(max_length=255)
    kota_kabupaten = models.CharField(max_length=255)   
    kecamatan = models.CharField(max_length=255)
    kelurahan = models.CharField(max_length=255)
    jumlah_instruktur = models.IntegerField()
    jumlah_peserta = models.IntegerField()
    peserta_aktif = models.IntegerField()
    jumlah_latihan_per_minggu = models.IntegerField()
    link_gmap = models.URLField(max_length=500, blank=True, null=True)
    profile = models.ImageField(upload_to='sasana_profiles/', blank=True, null=True)

    def __str__(self):
        return self.nama_sasana
#    pengurus_daerah = models.ForeignKey(PengurusDaerah, on_delete=models.CASCADE)
#    pengurus_sasana = models.OneToOneField(PengurusSasana, on_delete=models.CASCADE)

class JadwalLatihan(models.Model):
    id_jadwal = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tanggal_latihan = models.DateField()
    jam_latihan = models.TimeField()
#    sasana = models.ForeignKey(Sasana, on_delete=models.CASCADE)

class Peserta(models.Model):
    id_peserta = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # nama_peserta = models.CharField(max_length=255)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Peserta (Akun Pengguna)", limit_choices_to={'level':1})
    tanggal_lahir_peserta = models.DateField()
    kendala_terapi = models.TextField()
    sasana = models.ForeignKey(Sasana, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.nama_peserta

class Instruktur(models.Model):
    id_instruktur = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    #peserta = models.OneToOneField(Peserta, on_delete=models.CASCADE, null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'level__in': [1, 2]})
    # sertifikasi = models.BooleanField()
    tanggal_sertifikasi = models.DateField(null=True, blank=True)
    file_sertifikat = models.FileField(upload_to='sertifikat_instruktur/', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=['pdf','png','jpg'])], help_text="Format yang diizinkan hanya PDF, PNG, dan JPG. Ukuran file maksimal 5MB.")
    sasana = models.ForeignKey(Sasana, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.user.username
    
@receiver(post_delete, sender=Instruktur)
def demote_user_on_instructor_delete(sender, instance, **kwargs):
    user_to_demote = instance.user
    user_to_demote.level = 1
    user_to_demote.save()

    Peserta.objects.create(user=user_to_demote, sasana=instance.sasana, tanggal_lahir_peserta='1000-01-01', kendala_terapi = 'Butuh diperbaiki.')

    print(f"PENGGUNA: {user_to_demote.username} telah dikembalikan menjadi Peserta.")
    
class PengurusSasana(models.Model):
    id_pengurus = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #peserta = models.OneToOneField(Peserta, on_delete=models.CASCADE)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Pengurus (Akun Pengguna)", limit_choices_to={'level': 3})
    # no_telp_pengurus_sasana = models.CharField(max_length=20)
    jabatan = models.CharField(max_length=100)
    sasana = models.ForeignKey(Sasana, on_delete=models.CASCADE, related_name='pengurus_sasana')

    def __str__(self):
        return f"{self.user.username} - {self.jabatan} di {self.sasana.nama_sasana}"

class Peraga(models.Model):
    id_peraga = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama_peraga = models.CharField(max_length=255)
    #sasana = models.ForeignKey(Sasana, on_delete=models.CASCADE)

class Pelatihan(models.Model):
    id_pelatihan = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama_pelatihan = models.CharField(max_length=255)
    tanggal_pelatihan = models.DateField()
    penyelenggara = models.CharField(max_length=255)
    deskripsi = models.TextField()
#    instruktur = models.ManyToManyField(Instruktur)

class Gerakan(models.Model):
    id_gerakan = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama_gerakan = models.CharField(max_length=255)
    deskripsi_acuan = models.TextField()
    referensi_gerakan = models.TextField()
#    peraga = models.ManyToManyField(Peraga)

class Evaluasi(models.Model):
#    id_evaluasi = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#    peserta = models.ForeignKey(Sasana, on_delete=models.CASCADE)
#    gerakan = models.ForeignKey(Sasana, on_delete=models.CASCADE)
    tanggal_evaluasi = models.DateField()
    periode_evaluasi = models.DateField()
    hasil_evaluasi = models.TextField()


# API
class Provinsi(models.Model):
    id = models.IntegerField(primary_key=True)
    nama = models.CharField(max_length=255)

    def __str__(self):
        return self.nama

class Kabupaten(models.Model):
    id = models.IntegerField(primary_key=True)
    provinsi = models.ForeignKey(Provinsi, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255)

    def __str__(self):
        return self.nama
    
class Kecamatan(models.Model):
    id = models.IntegerField(primary_key=True)
    kabupaten = models.ForeignKey(Kabupaten, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255)

    def __str__(self):
        return self.nama

class Kelurahan(models.Model):
    id = models.IntegerField(primary_key=True)
    kecamatan = models.ForeignKey(Kecamatan, on_delete=models.CASCADE)
    nama = models.CharField(max_length=255)

    def __str__(self):
        return self.nama