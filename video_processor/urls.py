from django.urls import path
from . import views

urlpatterns = [
    path('test', views.upload_and_predict, name='upload_page'),
]