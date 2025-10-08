from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.productos_list, name='productos_list'),
    path('nuevo/', views.productos_create, name='productos_create'),
    path('<int:pk>/editar/', views.productos_edit, name='productos_edit'),
    path('<int:pk>/eliminar/', views.productos_delete, name='productos_delete'),
]
