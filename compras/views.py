from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.forms import inlineformset_factory
from .models import Compra, DetalleCompra
from .forms import CompraForm, DetalleCompraForm
from django.contrib import messages
from django.db.models import Q



def compras_list(request):
    query = request.GET.get('q', '').strip()
    compras = Compra.objects.all().order_by('-fecha')

    if query:
        compras = compras.filter(
            Q(numero_factura__icontains=query) |
            Q(proveedor_fk__nombre__icontains=query)
        )

    return render(request, 'compras/compras_list.html', {
        'compras': compras,
        'query': query
    })



def compras_create(request):
    DetalleFormSet = inlineformset_factory(
        Compra, DetalleCompra, form=DetalleCompraForm, extra=3, can_delete=True
        )

    if request.method == 'POST':
        form = CompraForm(request.POST)
        formset = DetalleFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            compra = form.save()
            detalles = formset.save(commit=False)
            total = 0
            for detalle in detalles:
                detalle.compra = compra
                detalle.save()
                total += detalle.subtotal
            compra.total = total
            compra.save()
            messages.success(request, 'Compra registrada exitosamente.')
            return redirect('compras:compras_list')
    else:
        form = CompraForm()
        formset = DetalleFormSet()

    return render(request, 'compras/compras_create.html', {
        'form': form,
        'formset': formset
    })

# --- Ver eliminar de una compra ---
@require_POST
def compras_delete(request, pk):
    compra = get_object_or_404(Compra, pk=pk)
    compra.delete()
    messages.success(request, 'Compra eliminada correctamente.')
    return redirect('compras:compras_list')


# --- Ver detalle de una compra ---
def compras_detail(request, pk):
    compra = get_object_or_404(Compra, pk=pk)
    detalles = compra.detalles.all()
    return render(request, 'compras/compras_detail.html', {
        'compra': compra,
        'detalles': detalles
    })




# --- Editar compra ---
def compras_edit(request, pk):
    compra = get_object_or_404(Compra, pk=pk)

    DetalleFormSet = inlineformset_factory(
        Compra, DetalleCompra, form=DetalleCompraForm, extra=1, can_delete=True
    )

    if request.method == "POST":
        form = CompraForm(request.POST, instance=compra)
        formset = DetalleFormSet(request.POST, instance=compra)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect("compras:compras_list")
        else:
            print("Error al editar compra")
            print(form.errors)
            print(formset.errors)

    else:
        form = CompraForm(instance=compra)
        formset = DetalleFormSet(instance=compra)

    return render(
        request,
        "compras/compras_edit.html",
        {"form": form, "formset": formset, "compra": compra},
    )
