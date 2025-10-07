from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

ROLES = [
    ("ADMIN", [
        # Admin tendrá todos los permisos; asignamos todo luego en admin o aquí:
        # Podemos dejar vacío y confiar en is_superuser para el superusuario.
    ]),
    ("VENTAS", []),
    ("ALMACEN", []),
    ("COMPRAS", []),
    ("PRODUCCION", []),
]

class Command(BaseCommand):
    help = "Crea grupos/roles base"

    def handle(self, *args, **kwargs):
        for role_name, perm_codenames in ROLES:
            group, created = Group.objects.get_or_create(name=role_name)
            if perm_codenames:
                perms = Permission.objects.filter(codename__in=perm_codenames)
                group.permissions.set(perms)
            self.stdout.write(self.style.SUCCESS(f"✓ Grupo {role_name} listo"))
