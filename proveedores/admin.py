from django.contrib import admin
from .models import Proveedor

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'nit', 'tipo', 'activo')
    search_fields = ('codigo', 'nombre', 'nit', 'correo', 'telefono')
    list_filter = ('tipo', 'activo')
