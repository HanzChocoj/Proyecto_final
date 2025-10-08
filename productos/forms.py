from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        exclude = ['codigo', 'fecha_creacion', 'ultima_actualizacion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'costo': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}), 
            'unidad_medida': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'categoria': 'Categoría',
            'unidad_medida': 'Unidad de medida',
        }

