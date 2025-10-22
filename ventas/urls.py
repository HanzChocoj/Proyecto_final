from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.ventas_list, name='ventas_list'),
    path('nueva/', views.ventas_create, name='ventas_create'),
    path('<int:pk>/editar/', views.ventas_edit, name='ventas_edit'),
    path('<int:pk>/eliminar/', views.ventas_delete, name='ventas_delete'),
    path('<int:pk>/pdf/', views.venta_pdf, name='venta_pdf'),
    path('obtener_precio_producto/', views.obtener_precio_producto, name='obtener_precio_producto'),
]
