from django.shortcuts import render, redirect, get_object_or_404
from .models import Cliente
from .forms import ClienteForm
from django.db.models import Q



def cliente_list(request):
    query = request.GET.get('q', '').strip()
    clientes = Cliente.objects.all()

    if query:
        clientes = clientes.filter(
            Q(nombre__icontains=query) |
            Q(nit__icontains=query) |
            Q(telefono__icontains=query) |
            Q(codigo__icontains=query)
        )

    return render(request, 'clientes/cliente_list.html', {
        'clientes': clientes,
        'query': query
    })



def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clientes:cliente_list')
    else:
        form = ClienteForm()
    return render(request, 'clientes/cliente_form.html', {'form': form, 'accion': 'Nuevo'})

def cliente_edit(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('clientes:cliente_list')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/cliente_form.html', {'form': form, 'accion': 'Editar'})

def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        return redirect('clientes:cliente_list')
    return render(request, 'clientes/cliente_confirm_delete.html', {'cliente': cliente})
