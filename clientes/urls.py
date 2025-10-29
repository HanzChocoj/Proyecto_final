from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('', views.cliente_list, name='cliente_list'),
    path('nuevo/', views.cliente_create, name='cliente_create'),
    path('<int:pk>/editar/', views.cliente_edit, name='cliente_edit'),
    path('<int:pk>/eliminar/', views.cliente_delete, name='cliente_delete'),
]
