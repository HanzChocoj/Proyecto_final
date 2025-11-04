from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import Receta, OrdenProduccion
from .forms import RecetaForm, DetalleRecetaFormSet, OrdenProduccionForm


# ==========================================
# 📘 RECETAS
# ==========================================


def recetas_list(request):
    query = request.GET.get('q', '').strip()
    recetas = Receta.objects.all().order_by('-id')

    if query:
        recetas = recetas.filter(
            Q(nombre__icontains=query) |
            Q(producto_final__nombre__icontains=query)
        )

    return render(request, 'produccion/recetas_list.html', {
        'recetas': recetas,
        'query': query
    })



@transaction.atomic
def receta_create(request):
    form = RecetaForm(request.POST or None)

    # 🧩 Formset con 6 líneas de insumos por defecto
    DetalleRecetaFormSetExtra = DetalleRecetaFormSet
    DetalleRecetaFormSetExtra.extra = 6
    formset = DetalleRecetaFormSetExtra(request.POST or None)

    if request.method == "POST":
        if form.is_valid() and formset.is_valid():
            receta = form.save()
            detalles = formset.save(commit=False)
            for d in detalles:
                d.receta = receta
                d.save()
            messages.success(request, "Receta creada correctamente.")
            return redirect('produccion:recetas_list')
        else:
            messages.error(request, "Corrige los errores del formulario.")

    return render(request, 'produccion/receta_form.html', {
        'form': form, 'formset': formset, 'accion': 'Crear'
    })


@transaction.atomic
def receta_edit(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    form = RecetaForm(request.POST or None, instance=receta)
    formset = DetalleRecetaFormSet(request.POST or None, instance=receta)

    if request.method == "POST":
        if form.is_valid() and formset.is_valid():
            receta = form.save(commit=False)
            receta.save()

            # Guardamos los insumos
            detalles = formset.save(commit=False)
            for d in detalles:
                d.receta = receta
                d.save()

            # Eliminamos los que fueron marcados con “X”
            for obj in formset.deleted_objects:
                obj.delete()

            messages.success(request, f"✅ Receta #{receta.id} actualizada correctamente.")
            return redirect('produccion:recetas_list')
        else:
            # Mostrar errores de validación del form o formset
            print("ERRORES FORM:", form.errors)
            print("ERRORES FORMSET:", formset.errors)
            messages.error(request, "⚠️ Corrige los errores antes de guardar los cambios.")

    return render(request, 'produccion/receta_form.html', {
        'form': form,
        'formset': formset,
        'accion': 'Editar'
    })


# ==========================================
#  ÓRDENES DE PRODUCCIÓN
# ==========================================


def ordenes_list(request):
    query = request.GET.get('q', '').strip()
    ordenes = OrdenProduccion.objects.select_related('receta', 'receta__producto_final').order_by('-fecha')

    if query:
        ordenes = ordenes.filter(
            Q(receta__nombre__icontains=query) |
            Q(receta__producto_final__nombre__icontains=query) |
            Q(encargado__username__icontains=query)
        )

    return render(request, 'produccion/ordenes_list.html', {
        'ordenes': ordenes,
        'query': query
    })


@transaction.atomic
def orden_create(request):
    form = OrdenProduccionForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            orden = form.save(commit=False)
            if request.user.is_authenticated:
                orden.encargado = request.user
            orden.save()
            messages.success(request, "Orden de producción creada en estado BORRADOR.")
            return redirect('produccion:ordenes_list')
        else:
            messages.error(request, "Corrige los errores antes de guardar.")

    return render(request, 'produccion/orden_form.html', {'form': form})


def orden_detail(request, pk):
    orden = get_object_or_404(OrdenProduccion, pk=pk)
    return render(request, 'produccion/orden_detail.html', {'orden': orden})


@transaction.atomic
def orden_confirmar(request, pk):
    orden = get_object_or_404(OrdenProduccion, pk=pk)
    try:
        orden.confirmar()
        messages.success(request, f"Orden #{orden.id} confirmada correctamente.")
    except ValidationError as e:
        messages.error(request, f"No se pudo confirmar: {e}")
    return redirect('produccion:orden_detail', pk=pk)


@transaction.atomic
def orden_anular(request, pk):
    orden = get_object_or_404(OrdenProduccion, pk=pk)
    try:
        orden.anular()
        messages.success(request, f"Orden #{orden.id} anulada y stock revertido.")
    except ValidationError as e:
        messages.error(request, f"No se pudo anular: {e}")
    return redirect('produccion:orden_detail', pk=pk)
