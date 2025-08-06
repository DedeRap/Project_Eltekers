# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager

class CustomUser(AbstractUser):
    LEVEL_CHOICES = ((1, 'Peserta'), (2, 'Instruktur'), (3, 'Pengurus Sasana'), (4, 'Pengurus Daerah'), (5, 'Admin'))
    level = models.IntegerField(choices=LEVEL_CHOICES, default=1)
    # Tambahkan field lain jika perlu di sini

    email = models.EmailField(blank=True, null=True)

    nomor_telepon = models.CharField(max_length=15, unique=True, null=False, blank=False)
    
    REQUIRED_FIELDS = ['nomor_telepon']
    
    objects = CustomUserManager()

    def __str__(self):
        return self.username