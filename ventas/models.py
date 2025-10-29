from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.exceptions import ValidationError
from productos.models import Producto
from clientes.models import Cliente

class Venta(models.Model):
    fecha = models.DateField(auto_now_add=True, verbose_name="Fecha de venta")


    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="ventas",
        verbose_name="Cliente"
    )
    
    numero_documento = models.CharField(max_length=50, unique=True, verbose_name="No. Documento", editable=False)
    encargado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Vendedor/Encargado"
    )
    comentarios = models.TextField(blank=True, null=True, verbose_name="Comentarios / Observaciones")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"Venta #{self.id} - {self.numero_documento} - {self.cliente}"

    def calcular_total(self):
        """Recalcula el total con base en los detalles existentes."""
        total = Decimal('0.00')
        for d in self.detalles.all():
            total += (d.cantidad or 0) * (d.precio_unitario or 0)
        self.total = total

    def save(self, *args, **kwargs):
        """Genera número correlativo y evita calcular antes de tener ID."""
        is_new = self.pk is None

        # Generar automáticamente el número de documento si no existe
        if not self.numero_documento:
            ultimo = Venta.objects.order_by('-id').first()
            if ultimo and ultimo.numero_documento.isdigit():
                self.numero_documento = str(int(ultimo.numero_documento) + 1)
            else:
                self.numero_documento = "1000001"

        super().save(*args, **kwargs)
        self.calcular_total()
        super().save(update_fields=['total'])

    def delete(self, *args, **kwargs):
        """Cuando se elimina una venta, se devuelve el stock de todos sus productos."""
        for detalle in self.detalles.all():
            try:
                detalle._revert_effect(detalle.producto, detalle.cantidad)
            except Exception as e:
                print(f"⚠️ Error al revertir stock del producto {detalle.producto}: {e}")
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha', '-id']



class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    def clean(self):
        """Evita vender más producto del stock disponible."""
        if self.producto and self.cantidad:
            disponible = self.producto.stock or 0
            if self.pk:
                prev = DetalleVenta.objects.get(pk=self.pk)
                disponible += prev.cantidad
            if self.cantidad > disponible:
                raise ValidationError({
                    'cantidad': f"Stock insuficiente. Solo hay {disponible} unidades disponibles."
                })


    def _apply_effect(self, producto, cantidad):
        """Descuenta stock solo a través de Kardex."""
        if cantidad and producto:
            try:
                from kardex.utils import registrar_movimiento
                registrar_movimiento(producto, 'SALIDA', int(cantidad), f"Venta #{self.venta.numero_documento}")
            except Exception as e:
                print(f"⚠️ No se pudo registrar movimiento Kardex (venta): {e}")

    def _revert_effect(self, producto, cantidad):
        """Devuelve stock solo a través de Kardex."""
        if cantidad and producto:
            try:
                from kardex.utils import registrar_movimiento
                registrar_movimiento(producto, 'ENTRADA', int(cantidad), f"Reversión venta #{self.venta.numero_documento}")
            except Exception as e:
                print(f"⚠️ No se pudo registrar reversión en Kardex: {e}")



    def save(self, *args, **kwargs):
        """Controla el impacto de stock al crear o editar."""
        self.full_clean()
        is_new = self.pk is None

        if is_new:
            super().save(*args, **kwargs)
            self._apply_effect(self.producto, self.cantidad)
        else:
            previous = DetalleVenta.objects.get(pk=self.pk)
            prev_prod = previous.producto
            prev_qty = previous.cantidad
            super().save(*args, **kwargs)

            if prev_prod != self.producto:
                self._revert_effect(prev_prod, prev_qty)
                self._apply_effect(self.producto, self.cantidad)
            else:
                delta = self.cantidad - prev_qty
                if delta != 0:
                    if delta > 0:
                        self._apply_effect(self.producto, delta)
                    else:
                        self._revert_effect(self.producto, abs(delta))

        self.venta.calcular_total()
        self.venta.save(update_fields=["total"])

    def delete(self, *args, **kwargs):
        """Devuelve el stock cuando se elimina un detalle."""
        prod = self.producto
        qty = self.cantidad
        venta = self.venta

        self._revert_effect(prod, qty)
        super().delete(*args, **kwargs)
        venta.calcular_total()
        venta.save(update_fields=["total"])

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"

    class Meta:
        verbose_name = "Detalle de venta"
        verbose_name_plural = "Detalles de venta"
