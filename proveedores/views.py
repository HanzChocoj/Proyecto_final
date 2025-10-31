from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Proveedor
from .forms import ProveedorForm

def proveedores_list(request):
    q = request.GET.get('q', '').strip()
    proveedores = Proveedor.objects.all()
    if q:
        proveedores = proveedores.filter(
            Q(codigo__icontains=q) |
            Q(nombre__icontains=q) |
            Q(nit__icontains=q) |
            Q(correo__icontains=q)
        )
    proveedores = proveedores.order_by('nombre')
    return render(request, 'proveedores/proveedores_list.html', {
        'proveedores': proveedores,
        'q': q,
    })

def proveedor_create(request):
    form = ProveedorForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor creado correctamente.")
            return redirect('proveedores:proveedores_list')
        messages.error(request, "Corrige los errores.")
    return render(request, 'proveedores/proveedores_form.html', {'form': form, 'accion': 'Crear'})

def proveedor_edit(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    form = ProveedorForm(request.POST or None, instance=proveedor)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor actualizado correctamente.")
            return redirect('proveedores:proveedores_list')
        messages.error(request, "Corrige los errores.")
    return render(request, 'proveedores/proveedores_form.html', {'form': form, 'accion': 'Editar'})

def proveedor_delete(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        proveedor.delete()
        messages.success(request, "Proveedor eliminado.")
        return redirect('proveedores:proveedores_list')
    return render(request, 'proveedores/proveedores_confirm_delete.html', {'proveedor': proveedor})
