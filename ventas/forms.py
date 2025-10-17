from django import forms
from .models import Venta, DetalleVenta

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente', 'encargado', 'comentarios']

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'precio_unitario']
