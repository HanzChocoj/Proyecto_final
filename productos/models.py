from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Categoría")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']


class UnidadMedida(models.Model):
    nombre = models.CharField(max_length=20, unique=True, verbose_name="Unidad de medida")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Unidad de medida"
        verbose_name_plural = "Unidades de medida"
        ordering = ['nombre']


class Producto(models.Model):
    codigo = models.CharField(max_length=20, unique=True, editable=False, verbose_name="Código")
    nombre = models.CharField(max_length=100, verbose_name="Nombre del producto")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoría")
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Unidad de medida")
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Costo del producto")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio unitario")
    stock = models.PositiveIntegerField(default=0, verbose_name="Cantidad en inventario")
    stock_minimo = models.PositiveIntegerField(default=0, verbose_name="Stock mínimo")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    ultima_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    def save(self, *args, **kwargs):
        # Generar código automáticamente si es nuevo
        if not self.codigo:
            ultimo = Producto.objects.order_by('-id').first()
            if ultimo and ultimo.codigo.startswith('A-'):
                ultimo_num = int(ultimo.codigo.split('-')[1])
                nuevo_num = ultimo_num + 1
            else:
                nuevo_num = 1
            self.codigo = f"A-{nuevo_num:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    @property
    def margen(self):
        try:
            return float(self.precio) - float(self.costo)
        except (TypeError, ValueError):
            return 0.0

    @property
    def margen_porcentaje(self):
        try:
            if self.costo > 0:
                return round(((float(self.precio) - float(self.costo)) / float(self.costo)) * 100, 2)
            return 0.0
        except (TypeError, ValueError):
            return 0.0

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']
