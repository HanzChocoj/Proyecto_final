from django.contrib import admin
from .models import Producto, Categoria, UnidadMedida

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'codigo', 'nombre', 'categoria', 'unidad_medida',
        'precio', 'costo', 'stock', 'stock_minimo',
        'activo', 'ultima_actualizacion'
    )
    search_fields = ('codigo', 'nombre')
    list_filter = ('activo', 'categoria', 'unidad_medida')
    ordering = ('nombre',)
