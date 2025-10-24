from decimal import Decimal
from django.db import models, transaction
from django.conf import settings
from django.core.exceptions import ValidationError
from productos.models import Producto


class Receta(models.Model):
    """
    Receta (BOM): define los insumos requeridos para producir 1 unidad del producto_final.
    Ej.: Para 1 galón de CLORO LISTO, usar 0.005 toneladas de CLORO CONCENTRADO + 0.995 agua, etc.
    """
    producto_final = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name='recetas_como_final'
    )
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Receta {self.nombre} → {self.producto_final}"

    def total_items(self):
        return self.detalles.count()

    class Meta:
        verbose_name = "Receta"
        verbose_name_plural = "Recetas"
        unique_together = [('producto_final', 'nombre')]


class DetalleReceta(models.Model):
    """
    Cantidad de cada insumo para producir 1 unidad del producto_final de la receta.
    """
    receta = models.ForeignKey(
        Receta, on_delete=models.CASCADE, related_name='detalles'
    )
    insumo = models.ForeignKey(
        Producto, on_delete=models.PROTECT, related_name='insumo_en_recetas'
    )
    cantidad_por_unidad = models.DecimalField(max_digits=12, decimal_places=4)

    def __str__(self):
        return f"{self.insumo} x {self.cantidad_por_unidad} (por 1 unidad de {self.receta.producto_final})"

    def clean(self):
        if self.cantidad_por_unidad is None or self.cantidad_por_unidad <= 0:
            raise ValidationError({"cantidad_por_unidad": "Debe ser mayor a cero."})
        if self.insumo_id == self.receta.producto_final_id:
            raise ValidationError("El insumo no puede ser el mismo que el producto final.")

    class Meta:
        verbose_name = "Detalle de receta"
        verbose_name_plural = "Detalles de receta"
        unique_together = [('receta', 'insumo')]


class OrdenProduccion(models.Model):
    ESTADO_BORRADOR = 'BORRADOR'
    ESTADO_CONFIRMADA = 'CONFIRMADA'
    ESTADO_ANULADA = 'ANULADA'
    ESTADOS = [
        (ESTADO_BORRADOR, 'Borrador'),
        (ESTADO_CONFIRMADA, 'Confirmada'),
        (ESTADO_ANULADA, 'Anulada'),
    ]

    receta = models.ForeignKey(Receta, on_delete=models.PROTECT, related_name='ordenes')
    cantidad_a_producir = models.DecimalField(max_digits=12, decimal_places=4)
    fecha = models.DateTimeField(auto_now_add=True)
    encargado = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    comentarios = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=12, choices=ESTADOS, default=ESTADO_BORRADOR)

    def __str__(self):
        return f"OP #{self.id} ({self.receta.producto_final}) x {self.cantidad_a_producir} – {self.estado}"

    # --------- Validaciones base ---------
    def clean(self):
        if self.cantidad_a_producir is None or self.cantidad_a_producir <= 0:
            raise ValidationError({"cantidad_a_producir": "Debe ser mayor a cero."})
        if not self.receta.activo:
            raise ValidationError("La receta está inactiva y no puede usarse.")

    # --------- Cálculos de consumo ---------
    def consumos_necesarios(self):
        """
        Devuelve lista de (Producto insumo, Decimal cantidad_necesaria) para esta orden.
        Se calcula multiplicando cada 'cantidad_por_unidad' por 'cantidad_a_producir'.
        """
        multiplicador = Decimal(self.cantidad_a_producir or 0)
        resultados = []
        for det in self.receta.detalles.select_related('insumo'):
            necesarios = (det.cantidad_por_unidad or 0) * multiplicador
            resultados.append((det.insumo, necesarios))
        return resultados

    def producto_final(self):
        return self.receta.producto_final

    # --------- Chequeo de stock antes de confirmar ---------
    def _verificar_stock(self):
        """
        Lanza ValidationError si no hay stock suficiente de algún insumo.
        """
        errores = []
        for insumo, qty in self.consumos_necesarios():
            disponible = insumo.stock or 0
            if qty > disponible:
                errores.append(f"• {insumo} – requerido: {qty}, disponible: {disponible}")
        if errores:
            raise ValidationError({"insumos": ["Stock insuficiente:\n" + "\n".join(errores)]})

    # --------- Aplicar / revertir movimientos de inventario ---------
    def _aplicar_movimientos(self):
        """
        Descuenta insumos y suma producto final al confirmar.
        """
        # Descontar insumos
        for insumo, qty in self.consumos_necesarios():
            insumo.stock = (insumo.stock or 0) - Decimal(qty)
            insumo.save(update_fields=['stock'])

        # Sumar producto final
        pf = self.producto_final()
        pf.stock = (pf.stock or 0) + Decimal(self.cantidad_a_producir or 0)
        pf.save(update_fields=['stock'])

    def _revertir_movimientos(self):
        """
        Revierte la confirmación: devuelve insumos y descuenta producto final.
        Solo se usa al ANULAR.
        """
        # Devolver insumos
        for insumo, qty in self.consumos_necesarios():
            insumo.stock = (insumo.stock or 0) + Decimal(qty)
            insumo.save(update_fields=['stock'])

        # Descontar producto final
        pf = self.producto_final()
        pf.stock = (pf.stock or 0) - Decimal(self.cantidad_a_producir or 0)
        pf.save(update_fields=['stock'])

    # --------- Acciones de estado ---------
    @transaction.atomic
    def confirmar(self):
        """
        Pasa de BORRADOR → CONFIRMADA, aplicando movimientos de inventario.
        """
        if self.estado != self.ESTADO_BORRADOR:
            raise ValidationError("Solo se pueden confirmar órdenes en estado BORRADOR.")
        self.clean()
        self._verificar_stock()
        self._aplicar_movimientos()
        self.estado = self.ESTADO_CONFIRMADA
        self.save(update_fields=['estado'])

    @transaction.atomic
    def anular(self):
        """
        Pasa de CONFIRMADA → ANULADA, revirtiendo movimientos de inventario.
        """
        if self.estado != self.ESTADO_CONFIRMADA:
            raise ValidationError("Solo se pueden anular órdenes CONFIRMADAS.")
        self._revertir_movimientos()
        self.estado = self.ESTADO_ANULADA
        self.save(update_fields=['estado'])

    class Meta:
        verbose_name = "Orden de producción"
        verbose_name_plural = "Órdenes de producción"
        ordering = ['-fecha', '-id']
