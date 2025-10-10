from django.urls import path
from . import views

app_name = "compras"

urlpatterns = [
    path('', views.compras_list, name='compras_list'),
    path('nueva/', views.compras_create, name='compras_create'),
    path('<int:pk>/', views.compras_detail, name='compras_detail'),
    path('<int:pk>/editar/', views.compras_edit, name='compras_edit'),
    path('<int:pk>/eliminar/', views.compras_delete, name='compras_delete'),
]
