from django.urls import path
from . import views

app_name = 'kardex'

urlpatterns = [
    path('', views.kardex_list, name='kardex_list'),
]
