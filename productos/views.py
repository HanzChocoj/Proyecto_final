from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Producto
from .forms import ProductoForm


@login_required
def productos_list(request):
    productos = Producto.objects.all()
    return render(request, 'productos/productos_list.html', {'productos': productos})


@login_required
def productos_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('productos:productos_list')
    else:
        form = ProductoForm()
    return render(request, 'productos/productos_create.html', {'form': form})


@login_required
def productos_edit(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('productos:productos_list')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/productos_edit.html', {'form': form, 'producto': producto})


@login_required
def productos_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('productos:productos_list')
    return render(request, 'productos/productos_confirm_delete.html', {'producto': producto})
