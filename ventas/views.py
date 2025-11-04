from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from productos.models import Producto
from .models import Venta, DetalleVenta
from .forms import VentaForm, DetalleVentaForm
from django.utils.timezone import now
from .utils import render_to_pdf
from django.db import models 
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Q

def ventas_list(request):
    query = request.GET.get('q', '').strip()
    ventas = Venta.objects.all().order_by('-fecha', '-id')

    if query:
        ventas = ventas.filter(
            Q(numero_documento__icontains=query) |
            Q(cliente__nombre__icontains=query)
        )

    return render(request, 'ventas/ventas_list.html', {
        'ventas': ventas,
        'query': query
    })


# ======================
# CREAR NUEVA VENTA
# ======================
def ventas_create(request):
    DetalleFormSet = inlineformset_factory(
        Venta, DetalleVenta, form=DetalleVentaForm, extra=1, can_delete=True
    )

    if request.method == 'POST':
        form = VentaForm(request.POST)

        if form.is_valid():
            venta = form.save(commit=False)
            if not venta.encargado and request.user.is_authenticated:
                venta.encargado = request.user
            venta.save()  # guardamos primero la venta (para tener ID)

            formset = DetalleFormSet(request.POST, instance=venta)

            if formset.is_valid():
                try:
                    detalles_validos = 0
                    detalles = formset.save(commit=False)

                    for d in detalles:
                        d.venta = venta
                        try:
                            d.save()  # valida stock dentro del modelo
                            detalles_validos += 1
                        except ValidationError as e:
                            producto_nombre = (
                                d.producto.nombre if hasattr(d.producto, 'nombre') else str(d.producto)
                            )
                            error_texto = next(iter(e.message_dict.get('cantidad', e.messages)), str(e))
                            messages.error(
                                request,
                                f" Stock insuficiente para '{producto_nombre}': {error_texto}",
                            )
                            venta.delete()
                            formset = DetalleFormSet(request.POST)
                            return render(
                                request,
                                'ventas/ventas_create.html',
                                {'form': form, 'formset': formset},
                            )

                    for obj in formset.deleted_objects:
                        obj.delete()

                    if detalles_validos == 0:
                        venta.delete()
                        messages.error(request, " La venta debe tener al menos un producto válido.")
                        return render(
                            request,
                            'ventas/ventas_create.html',
                            {'form': form, 'formset': formset},
                        )

                    messages.success(
                        request,
                        f"Venta #{venta.numero_documento} creada correctamente.",
                    )
                    return redirect('ventas:ventas_list')

                except Exception as e:
                    venta.delete()
                    messages.error(request, f" Error inesperado: {e}")
                    formset = DetalleFormSet(request.POST)
                    return render(
                        request,
                        'ventas/ventas_create.html',
                        {'form': form, 'formset': formset},
                    )

            else:
                venta.delete()
                errores_detalle = []
                for idx, error in enumerate(formset.errors, start=1):
                    if error:
                        errores_detalle.append(f"• Línea {idx}: {error}")

                if errores_detalle:
                    mensaje_error = "<br>".join(errores_detalle)
                    messages.error(request, f" Errores en los productos:<br>{mensaje_error}")
                else:
                    messages.error(request, " Corrige los errores en los productos antes de guardar.")

                return render(
                    request,
                    'ventas/ventas_create.html',
                    {'form': form, 'formset': formset},
                )

        else:
            messages.error(request, " Corrige los errores en el encabezado de la venta.")
            formset = DetalleFormSet(request.POST)
            return render(
                request,
                'ventas/ventas_create.html',
                {'form': form, 'formset': formset},
            )

    else:
        form = VentaForm()
        formset = DetalleFormSet()

    return render(request, 'ventas/ventas_create.html', {'form': form, 'formset': formset})


def venta_pdf(request, pk):
    venta = get_object_or_404(
        Venta.objects.select_related('encargado').prefetch_related('detalles__producto'),
        pk=pk
    )
    detalles = venta.detalles.all().order_by('id')

    # Si agregas ?download=1 en la URL, forzamos descarga
    download = request.GET.get('download') == '1'

    context = {
        'venta': venta,
        'detalles': detalles,
        'now': now(),
    }
    filename = f"venta_{venta.numero_documento}.pdf"
    return render_to_pdf('ventas/pdf/venta_comprobante.html', context, download=download, filename=filename)



# ======================
# EDITAR VENTA EXISTENTE
# ======================
def ventas_edit(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    DetalleFormSet = inlineformset_factory(
        Venta, DetalleVenta, form=DetalleVentaForm, extra=0, can_delete=True
    )

    if request.method == 'POST':
        form = VentaForm(request.POST, instance=venta)
        formset = DetalleFormSet(request.POST, instance=venta)

        if form.is_valid() and formset.is_valid():
            try:
                venta = form.save(commit=False)
                venta.save()

                detalles_validos = 0
                detalles = formset.save(commit=False)

                for d in detalles:
                    d.venta = venta
                    try:
                        d.save()  # valida stock dentro del modelo
                        detalles_validos += 1
                    except ValidationError as e:
                        producto_nombre = (
                            d.producto.nombre if hasattr(d.producto, 'nombre') else str(d.producto)
                        )
                        error_texto = next(iter(e.message_dict.get('cantidad', e.messages)), str(e))
                        messages.error(
                            request,
                            f" Stock insuficiente para '{producto_nombre}': {error_texto}",
                        )
                        return render(
                            request,
                            'ventas/ventas_edit.html',
                            {'form': form, 'formset': formset, 'venta': venta},
                        )

                for obj in formset.deleted_objects:
                    obj.delete()

                if detalles_validos == 0:
                    messages.error(request, " La venta debe tener al menos un producto válido.")
                    return render(
                        request,
                        'ventas/ventas_edit.html',
                        {'form': form, 'formset': formset, 'venta': venta},
                    )

                messages.success(request, f" Venta #{venta.numero_documento} actualizada correctamente.")
                return redirect('ventas:ventas_list')

            except ValidationError as e:
                error_msg = "; ".join([f"{k}: {', '.join(v)}" for k, v in e.message_dict.items()])
                messages.error(request, f" Error al actualizar la venta: {error_msg}")

        else:
            # Mostrar errores detallados
            if not form.is_valid():
                messages.error(request, f" Error en encabezado: {form.errors}")
            if not formset.is_valid():
                messages.error(request, f" Error en detalle: {formset.errors}")

    else:
        form = VentaForm(instance=venta)
        formset = DetalleFormSet(instance=venta)

    return render(request, 'ventas/ventas_edit.html', {
        'form': form,
        'formset': formset,
        'venta': venta
    })


# ======================
# ELIMINAR VENTA
# ======================
@require_POST
def ventas_delete(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    venta.delete()  # al borrar líneas, cada línea regresa stock en delete()
    messages.success(request, "Venta eliminada y stock devuelto.")
    return redirect('ventas:ventas_list')


# ======================
# OBTENER PRECIO DE PRODUCTO
# ======================
def obtener_precio_producto(request):
    """Devuelve el precio unitario del producto seleccionado."""
    producto_id = request.GET.get('producto_id')
    try:
        producto = Producto.objects.get(id=producto_id)
        return JsonResponse({'precio': float(producto.precio)})
    except Producto.DoesNotExist:
        return JsonResponse({'precio': 0})
