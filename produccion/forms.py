from django import forms
from django.forms import inlineformset_factory
from .models import Receta, DetalleReceta, OrdenProduccion


# -------------------------------
# FORMULARIO DE RECETA
# -------------------------------
class RecetaForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ["nombre", "producto_final", "descripcion", "activo"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }


class DetalleRecetaForm(forms.ModelForm):
    class Meta:
        model = DetalleReceta
        fields = ["insumo", "cantidad_por_unidad"]


# Formset para agregar varios insumos en una receta
DetalleRecetaFormSet = inlineformset_factory(
    Receta,
    DetalleReceta,
    form=DetalleRecetaForm,
    extra=1,
    can_delete=True
)


# -------------------------------
# FORMULARIO DE ORDEN DE PRODUCCIÓN
# -------------------------------
class OrdenProduccionForm(forms.ModelForm):
    class Meta:
        model = OrdenProduccion
        fields = ["receta", "cantidad_a_producir", "comentarios"]
        widgets = {
            "comentarios": forms.Textarea(attrs={"rows": 3}),
        }
