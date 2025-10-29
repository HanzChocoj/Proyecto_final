from django.utils import timezone
from kardex.models import MovimientoInventario

def registrar_movimiento(producto, tipo, cantidad, referencia):
    """
    Registra un movimiento en el Kardex.
    tipo = 'ENTRADA' o 'SALIDA'
    """

    if not producto or not cantidad:
        return

    #  Forzamos a obtener el stock real desde la base de datos
    producto.refresh_from_db(fields=['stock'])

    saldo_anterior = producto.stock or 0

    if tipo == 'ENTRADA':
        nuevo_saldo = saldo_anterior + cantidad
    elif tipo == 'SALIDA':
        nuevo_saldo = saldo_anterior - cantidad
    else:
        raise ValueError("Tipo de movimiento no válido. Use 'ENTRADA' o 'SALIDA'.")

    #  Registrar el movimiento
    MovimientoInventario.objects.create(
        producto=producto,
        tipo=tipo,
        cantidad=cantidad,
        saldo=nuevo_saldo,
        referencia=referencia,
        fecha=timezone.now(),
    )

    #  Actualizar el stock real del producto
    producto.stock = nuevo_saldo
    producto.save(update_fields=['stock'])
