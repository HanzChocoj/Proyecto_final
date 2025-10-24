from django.urls import path
from . import views

app_name = "produccion"

urlpatterns = [
    # Recetas
    path("recetas/", views.recetas_list, name="recetas_list"),
    path("recetas/nueva/", views.receta_create, name="receta_create"),
    path("recetas/<int:pk>/editar/", views.receta_edit, name="receta_edit"),

    # Órdenes de producción
    path("ordenes/", views.ordenes_list, name="ordenes_list"),
    path("ordenes/nueva/", views.orden_create, name="orden_create"),
    path("ordenes/<int:pk>/detalle/", views.orden_detail, name="orden_detail"),
    path("ordenes/<int:pk>/confirmar/", views.orden_confirmar, name="orden_confirmar"),
    path("ordenes/<int:pk>/anular/", views.orden_anular, name="orden_anular"),
]
