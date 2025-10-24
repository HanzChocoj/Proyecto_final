from django.shortcuts import render
from productos.models import Producto
from .models import MovimientoInventario

def kardex_list(request):
    producto_id = request.GET.get('producto')
    productos = Producto.objects.all().order_by('nombre')
    movimientos = []

    if producto_id:
        movimientos = MovimientoInventario.objects.filter(producto_id=producto_id).order_by('-fecha')

    return render(request, 'kardex/kardex_list.html', {
        'productos': productos,
        'movimientos': movimientos,
        'producto_id': producto_id,
    })
