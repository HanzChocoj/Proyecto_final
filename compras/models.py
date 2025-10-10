from django.db import models
from productos.models import Producto
from django.conf import settings
from decimal import Decimal

class Compra(models.Model):
    fecha = models.DateField(auto_now_add=True, verbose_name="Fecha de compra")
    proveedor = models.CharField(max_length=100, verbose_name="Proveedor")
    numero_factura = models.CharField(max_length=50, unique=True, verbose_name="Número de factura")

    encargado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Encargado de compra"
    )

    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")

    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Total compra")

    def save(self, *args, **kwargs):
        """Guarda la compra y actualiza automáticamente el total con base en los detalles."""
        super().save(*args, **kwargs)  # Guarda primero para tener ID disponible
        total = sum(
            detalle.cantidad * detalle.costo_unitario
            for detalle in self.detalles.all()
        )
        self.total = round(total, 2)
        super().save(update_fields=["total"])

    def __str__(self):
        return f"{self.numero_factura} - {self.proveedor}"

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ['-fecha']




class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cantidad")
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo unitario")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Subtotal", editable=False)

    def _set_stock_and_cost(self, prod, new_stock, new_cost):
        """Asigna stock/costo respetando el tipo de campo de stock del Producto."""
        # stock en Producto es PositiveIntegerField en tu modelo
        prod.stock = int(new_stock) if new_stock > 0 else 0
        prod.costo = (Decimal(new_cost).quantize(Decimal('0.01'))) if new_stock > 0 else Decimal('0.00')
        prod.save()

    def _apply_effect(self, prod, qty, unit_cost):
        """Aplica el efecto de una compra al producto (suma qty y recalcula costo promedio)."""
        S_prev = Decimal(prod.stock)
        C_prev = Decimal(prod.costo)
        qty = Decimal(qty)
        unit_cost = Decimal(unit_cost)

        S_new = S_prev + qty
        if S_new <= 0:
            self._set_stock_and_cost(prod, 0, 0)
            return

        value_new = (S_prev * C_prev) + (qty * unit_cost)
        C_new = value_new / S_new
        self._set_stock_and_cost(prod, S_new, C_new)

    def _revert_effect(self, prod, qty, unit_cost):
        """Revierte el efecto de una compra previa (resta qty y recalcula costo original)."""
        S_prev = Decimal(prod.stock)
        C_prev = Decimal(prod.costo)
        qty = Decimal(qty)
        unit_cost = Decimal(unit_cost)

        S0 = S_prev - qty
        if S0 <= 0:
            # Si al revertir queda en 0 o negativo, dejamos costo en 0 y stock en 0
            self._set_stock_and_cost(prod, 0, 0)
            return

        value_prev = S_prev * C_prev
        value0 = value_prev - (qty * unit_cost)
        C0 = value0 / S0
        self._set_stock_and_cost(prod, S0, C0)

    def save(self, *args, **kwargs):
        """
        Guarda el detalle:
        - Recalcula su subtotal.
        - Si es edición, revierte la línea anterior y aplica la nueva (maneja si cambiaste de producto).
        - Si es creación, solo aplica la nueva.
        - Finalmente recalcula el total del encabezado de compra.
        """
        # 1) Recalcular subtotal propio
        self.subtotal = self.cantidad * self.costo_unitario

        # Detectar si es edición y capturar el estado anterior
        old = None
        if self.pk:
            old = DetalleCompra.objects.select_related('producto', 'compra').get(pk=self.pk)

        super().save(*args, **kwargs)  # guarda el detalle (ya con nuevos valores)

        # 2) Ajustar inventario/costo promedio
        if old is None:
            # Creación: aplicar efecto nuevo
            self._apply_effect(self.producto, self.cantidad, self.costo_unitario)
        else:
            # Edición: revertir efecto anterior y aplicar el nuevo
            if old.producto_id != self.producto_id:
                # Revertir en el producto anterior
                self._revert_effect(old.producto, old.cantidad, old.costo_unitario)
                # Aplicar en el nuevo producto
                self._apply_effect(self.producto, self.cantidad, self.costo_unitario)
            else:
                # Mismo producto: revertir la línea anterior y aplicar la nueva
                self._revert_effect(self.producto, old.cantidad, old.costo_unitario)
                self._apply_effect(self.producto, self.cantidad, self.costo_unitario)

        # 3) Recalcular total del encabezado
        self.compra.save()

    def delete(self, *args, **kwargs):
        """
        Elimina el detalle revirtiendo su efecto sobre el producto
        y actualiza el total del encabezado.
        """
        prod = self.producto
        compra = self.compra
        # Revertir efecto de esta línea
        self._revert_effect(prod, self.cantidad, self.costo_unitario)
        super().delete(*args, **kwargs)
        # Recalcular total del encabezado
        compra.save()

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"

    class Meta:
        verbose_name = "Detalle de compra"
        verbose_name_plural = "Detalles de compra"
