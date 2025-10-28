from django.db import models
from productos.models import Producto


class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)  #  saldo acumulado
    referencia = models.CharField(max_length=255, blank=True, null=True)      #  origen del movimiento
    descripcion = models.CharField(max_length=255, blank=True, null=True)     #  detalle opcional
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.producto} - {self.tipo} ({self.cantidad})"

    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-fecha']
