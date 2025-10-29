from django.db import models

class Cliente(models.Model):
    TIPO_CHOICES = [
        ('MINORISTA', 'Minorista'),
        ('MAYORISTA', 'Mayorista'),
        ('DISTRIBUIDOR', 'Distribuidor'),
    ]

    codigo = models.CharField(max_length=10, unique=True, editable=False)  # autogenerado
    nombre = models.CharField(max_length=120)
    nit = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='MINORISTA')
    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """Genera código automático tipo C-00001 si no existe."""
        if not self.codigo:  # solo al crear
            ultimo = Cliente.objects.order_by('-id').first()
            if ultimo and ultimo.codigo.startswith('C-'):
                # extrae el número y le suma 1
                numero = int(ultimo.codigo.split('-')[1])
                nuevo_codigo = f"C-{numero + 1:05d}"
            else:
                nuevo_codigo = "C-00001"
            self.codigo = nuevo_codigo
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre']

