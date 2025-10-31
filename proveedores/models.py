from django.db import models

class Proveedor(models.Model):
    TIPO_CHOICES = [
        ('LOCAL', 'Local'),
        ('IMPORT', 'Importación'),
        ('SERV', 'Servicios'),
    ]

    codigo = models.CharField(max_length=10, unique=True, editable=False)
    nombre = models.CharField(max_length=120)
    nit = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='LOCAL')
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def save(self, *args, **kwargs):
        # Autogenerar código tipo P-00001
        if not self.codigo:
            last = Proveedor.objects.order_by('-id').first()
            if last and last.codigo and last.codigo.startswith('P-'):
                try:
                    corr = int(last.codigo.replace('P-', '')) + 1
                except Exception:
                    corr = self.id or 1
            else:
                corr = 1
            self.codigo = f"P-{corr:05d}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']
