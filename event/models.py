# events/models.py
from django.db import models
from django.conf import settings
from django.urls import reverse
from io import BytesIO
from django.core.files import File
import qrcode

class Event(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nama Event")
    date = models.DateField(verbose_name="Tanggal Event")
    # Field ini akan menyimpan gambar QR code yang dibuat secara otomatis
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True)
    # Relasi ke user yang membuat event (opsional tapi sangat direkomendasikan)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="events_created"
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Panggil method save() asli terlebih dahulu
        super().save(*args, **kwargs)

        # Hasilkan QR code hanya jika belum ada (saat pertama kali dibuat)
        if not self.qr_code:
            # Buat URL untuk halaman absensi event ini
            # 'event_attendance' adalah nama URL yang akan kita buat nanti
            attendance_url = reverse('event_attendance', args=[self.id])
            
            # Dapatkan URL lengkap (http://...)
            # Disarankan untuk mengatur domain situs Anda di settings.py
            full_url = f"http://127.0.0.1:8000{attendance_url}"

            # Buat gambar QR code
            qr_image = qrcode.make(full_url)
            canvas = qr_image.convert('RGB')
            
            # Simpan gambar ke buffer memori
            buffer = BytesIO()
            canvas.save(buffer, 'PNG')
            
            # Buat nama file dan simpan gambar ke field qr_code
            file_name = f'event-{self.id}-qr.png'
            self.qr_code.save(file_name, File(buffer), save=False)
            
            # Panggil save() lagi untuk menyimpan field qr_code yang baru
            super().save(update_fields=['qr_code'])