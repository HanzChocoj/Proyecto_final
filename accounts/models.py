from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        VENTAS = "VENTAS", "Ventas"
        ALMACEN = "ALMACEN", "Almacén"
        COMPRAS = "COMPRAS", "Compras"
        PRODUCCION = "PRODUCCION", "Producción"


    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.ADMIN)

    def full_name(self):
        # “Nombre completo”
        fn = (self.first_name or "").strip()
        ln = (self.last_name or "").strip()
        return (fn + " " + ln).strip() or self.username

    def __str__(self):
        return f"{self.username} ({self.role})"
