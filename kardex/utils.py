from django.utils import timezone
from kardex.models import MovimientoInventario
from decimal import Decimal


def registrar_movimiento(producto, tipo, cantidad, referencia):
    """
    Registra un movimiento en el Kardex y actualiza el saldo del producto.
    tipo = 'ENTRADA' o 'SALIDA'
    referencia = texto que describe el origen (ej: 'Venta #5', 'Compra #10', 'Producción #3')
    """

    if not producto or cantidad is None:
        return

    cantidad = Decimal(cantidad)

    # Obtener saldo anterior (último movimiento registrado)
    ultimo = MovimientoInventario.objects.filter(producto=producto).order_by('-fecha').first()
    saldo_anterior = ultimo.saldo if ultimo else Decimal(0)

    #  Calcular nuevo saldo
    if tipo == 'ENTRADA':
        nuevo_saldo = saldo_anterior + cantidad
    elif tipo == 'SALIDA':
        nuevo_saldo = saldo_anterior - cantidad
    else:
        raise ValueError("Tipo de movimiento no válido. Use 'ENTRADA' o 'SALIDA'.")

    #  Registrar el movimiento en Kardex
    MovimientoInventario.objects.create(
        producto=producto,
        tipo=tipo,
        cantidad=cantidad,
        saldo=nuevo_saldo,
        referencia=referencia,
        fecha=timezone.now(),
    )

    #  Sincronizar stock real del producto
    producto.stock = nuevo_saldo if nuevo_saldo >= 0 else 0
    producto.save(update_fields=["stock"])
