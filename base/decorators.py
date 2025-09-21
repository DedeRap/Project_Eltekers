from functools import wraps
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from .models import Sasana, PengurusSasana, Instruktur, Peserta

def user_is_authorized_for_sasana(view_func):
    @wraps(view_func)
    def _wrapped_view(request, id_sasana, *args, **kwargs):
        sasana = get_object_or_404(Sasana, id_sasana=id_sasana)
        user = request.user

        is_pengurus_daerah = (user.level == 4)

        is_pengurus_sasana_yang_sah = False
        if user.level == 3:
            is_pengurus_sasana_yang_sah = PengurusSasana.objects.filter(sasana=sasana, user=user).exists()

        if not (is_pengurus_daerah or is_pengurus_sasana_yang_sah):
            return HttpResponseForbidden("Anda tidak memiliki izin untuk mengakses data sasana ini.")
        
        return view_func(request, id_sasana, *args, **kwargs)
    
    return _wrapped_view

def user_is_authorized_for_pengurus(view_func):
    @wraps(view_func)
    def _wrapped_view(request, id_pengurus, *args, **kwargs):
        pengurus = get_object_or_404(PengurusSasana, id_pengurus=id_pengurus)
        sasana = pengurus.sasana
        user = request.user

        is_pengurus_daerah = (user.level == 4)

        if not is_pengurus_daerah:
            return HttpResponseForbidden("Anda tidak memiliki izin untuk mengedit data pengurus ini.")
        
        return view_func(request, id_pengurus, *args, **kwargs)
    
    return _wrapped_view

def user_is_authorized_for_pengurus_sasana_dan_instruktur(view_func):
    @wraps(view_func)
    def _wrapped_view(request, sasana_id, *args, **kwargs):
        sasana = get_object_or_404(Sasana, id_sasana=sasana_id)
        user = request.user
        
        # Variabel untuk menandai apakah pengguna diizinkan
        is_authorized = False
        
        if user.level == 3:
            is_authorized = PengurusSasana.objects.filter(sasana=sasana, user=user).exists()
        
        elif user.level == 2:
            is_authorized = Instruktur.objects.filter(sasana=sasana, user=user).exists()

        if not is_authorized:
            return HttpResponseForbidden("Anda tidak memiliki izin untuk mengakses data sasana ini.")
        
        return view_func(request, sasana_id, *args, **kwargs)
    
    return _wrapped_view

def user_is_authorized_for_pengurus_daerah_sasana_dan_instruktur(view_func):
    @wraps(view_func)
    def _wrapped_view(request, sasana_id, *args, **kwargs):
        sasana = get_object_or_404(Sasana, id_sasana=sasana_id)
        user = request.user
        
        # Variabel untuk menandai apakah pengguna diizinkan
        is_authorized = False

        if user.level == 4:
            is_authorized = True
        
        elif user.level == 3:
            is_authorized = PengurusSasana.objects.filter(sasana=sasana, user=user).exists()
        
        elif user.level == 2:
            is_authorized = Instruktur.objects.filter(sasana=sasana, user=user).exists()

        if not is_authorized:
            return HttpResponseForbidden("Anda tidak memiliki izin untuk mengakses data sasana ini.")
        
        return view_func(request, sasana_id, *args, **kwargs)
    
    return _wrapped_view

def user_is_authorized_for_instruktur_detail(view_func):
    @wraps(view_func)
    def _wrapped_view(request, id_instruktur, *args, **kwargs):
        
        instruktur = get_object_or_404(Instruktur, id_instruktur=id_instruktur)
        sasana = instruktur.sasana
        user = request.user

        is_authorized = False

        if user.level == 4: 
            is_authorized = True
        elif user.level == 3: 
            is_authorized = PengurusSasana.objects.filter(sasana=sasana, user=user).exists()

        if not is_authorized:
            return HttpResponseForbidden("Anda tidak memiliki izin untuk melihat detail instruktur ini.")
        
        return view_func(request, id_instruktur, *args, **kwargs)
    
    return _wrapped_view

def user_is_authorized_for_pengurus_sasana_data_instruktur(view_func):
    @wraps(view_func)
    def _wrapped_view(request, sasana_id, *args, **kwargs):
        sasana = get_object_or_404(Sasana, id_sasana=sasana_id)
        user = request.user
        
        # Variabel untuk menandai apakah pengguna diizinkan
        is_authorized = False
        
        if user.level == 3:
            is_authorized = PengurusSasana.objects.filter(sasana=sasana, user=user).exists()
        
        if not is_authorized:
            return HttpResponseForbidden("Anda tidak memiliki izin untuk mengakses data sasana ini.")
        
        return view_func(request, sasana_id, *args, **kwargs)
    
    return _wrapped_view

def user_is_authorized_for_pengurus_sasana_edit_instruktur(view_func):
    @wraps(view_func)
    def _wrapped_view(request, id_instruktur, *args, **kwargs):
        
        instruktur = get_object_or_404(Instruktur, id_instruktur=id_instruktur)
        sasana = instruktur.sasana
        user = request.user

        is_authorized = False

        if user.level == 3: 
            is_authorized = PengurusSasana.objects.filter(sasana=sasana, user=user).exists()

        if not is_authorized:
            return HttpResponseForbidden("Anda tidak memiliki izin untuk melihat detail instruktur ini.")
        
        return view_func(request, id_instruktur, *args, **kwargs)
    
    return _wrapped_view

def user_is_authorized_for_Peserta_with_id(view_func):
    @wraps(view_func)
    def _wrapped_view(request, id_peserta, *args, **kwargs):
        
        instruktur = get_object_or_404(Peserta, id_peserta=id_peserta)
        sasana = instruktur.sasana
        user = request.user

        is_authorized = False

        if user.level == 3: 
            is_authorized = PengurusSasana.objects.filter(sasana=sasana, user=user).exists()

        elif user.level == 2: 
            is_authorized = Instruktur.objects.filter(sasana=sasana, user=user).exists()

        if not is_authorized:
            return HttpResponseForbidden("Anda tidak memiliki izin untuk melihat detail instruktur ini.")
        
        return view_func(request, id_peserta, *args, **kwargs)
    
    return _wrapped_view