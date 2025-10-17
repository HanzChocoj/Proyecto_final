from django.contrib import admin
from .models import Venta, DetalleVenta

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha', 'numero_documento', 'cliente', 'total', 'encargado')
    fields = ('fecha', 'numero_documento', 'cliente', 'encargado', 'comentarios', 'total')
    readonly_fields = ('fecha', 'numero_documento', 'total')
    inlines = [DetalleVentaInline]