from django.contrib import admin
from .models import Receta, DetalleReceta, OrdenProduccion

class DetalleRecetaInline(admin.TabularInline):
    model = DetalleReceta
    extra = 0

@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "producto_final", "activo", "total_items")
    inlines = [DetalleRecetaInline]
    list_filter = ("activo",)
    search_fields = ("nombre", "producto_final__nombre")

@admin.register(OrdenProduccion)
class OrdenProduccionAdmin(admin.ModelAdmin):
    list_display = ("id", "receta", "cantidad_a_producir", "estado", "fecha", "encargado")
    list_filter = ("estado", "fecha")
    search_fields = ("receta__nombre", "receta__producto_final__nombre")
