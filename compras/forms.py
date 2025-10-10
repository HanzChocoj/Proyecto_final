from django import forms
from .models import Compra, DetalleCompra

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['proveedor', 'numero_factura', 'encargado', 'observaciones']
        widgets = {
            'proveedor': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_factura': forms.TextInput(attrs={'class': 'form-control'}),
            'encargado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'proveedor': 'Proveedor',
            'numero_factura': 'Número de Factura',
            'encargado': 'Encargado de compra',
            'observaciones': 'Observaciones',
        }

class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = ['producto', 'cantidad', 'costo_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'costo_unitario': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }
        labels = {
            'producto': 'Producto',
            'cantidad': 'Cantidad',
            'costo_unitario': 'Costo unitario',
        }
