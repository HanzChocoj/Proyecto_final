from django.urls import path
from . import views

app_name = 'proveedores'

urlpatterns = [
    path('', views.proveedores_list, name='proveedores_list'),
    path('nuevo/', views.proveedor_create, name='proveedor_create'),
    path('<int:pk>/editar/', views.proveedor_edit, name='proveedor_edit'),
    path('<int:pk>/eliminar/', views.proveedor_delete, name='proveedor_delete'),
]
