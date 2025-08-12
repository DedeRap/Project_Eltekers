from django.urls import path
from . import views

urlpatterns = [
    path('<int:event_id>/', views.event_detail_view, name='event_detail'),
    path('<int:event_id>/attend/', views.event_attendance_view, name='event_attendance'),
]