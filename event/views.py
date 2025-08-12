# events/views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Event

@login_required
def event_detail_view(request, event_id):
    # Pastikan hanya Pengurus Sasana (level 3) dan Instruktur (level 2) yang bisa akses
    if request.user.level not in [2, 3]:
        return HttpResponse("Anda tidak memiliki izin untuk melihat halaman ini.", status=403)
        
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/event_detail.html', {'event': event})


# View ini yang akan diakses saat peserta scan QR code
# Untuk saat ini, kita buat sederhana dulu
@login_required # Peserta juga harus login untuk absen
def event_attendance_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Di sini Anda akan menambahkan logika absensi di masa depan
    # Contoh:
    # Attendance.objects.create(user=request.user, event=event)
    
    return HttpResponse(f"Terima kasih! Kehadiran Anda untuk event '{event.name}' telah dicatat.")