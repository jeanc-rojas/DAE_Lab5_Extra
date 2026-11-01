"""Deja la tienda lista: catálogo, los dos grupos con los permisos de roles.py y sus usuarios.

Se puede repetir sin duplicar nada; repítelo cada vez que cambies roles.py (Parte 3a).
No crea el superusuario: eso es `createsuperuser`.
"""

from decimal import Decimal

from django.contrib.auth.models import Group, Permission, User
from django.core.management.base import BaseCommand
from django.utils import timezone

from tienda.grupos import GRUPO_AGENTE, GRUPO_REVISORES
from tienda.models import Categoria, Producto
from tienda.version import modulo

CATALOGO = {
    'Gaseosas': [('Fanta', '1.80', 0), ('Coca-Cola', '2.50', 24), ('Inca Kola', '2.50', 30)],
    'Galletas': [('Oreo', '1.20', 40), ('Soda Field', '0.80', 60)],
    'Snacks': [('Papas Lays', '1.50', 15)],
}
USUARIOS = [('asistente_ia', GRUPO_AGENTE), ('revisor', GRUPO_REVISORES)]


class Command(BaseCommand):
    help = 'Carga el catálogo y crea los grupos (con los permisos de roles.py) y los usuarios asistente_ia y revisor.'

    def add_arguments(self, parser):
        parser.add_argument('--clave', default='Tecsup2019', help='Contraseña de asistente_ia y revisor.')

    def handle(self, *args, clave, **options):
        ahora = timezone.now()
        for nombre_cat, productos in CATALOGO.items():
            cat, _ = Categoria.objects.get_or_create(nombre=nombre_cat, defaults={'pub_date': ahora})
            for nombre, precio, stock in productos:
                Producto.objects.get_or_create(
                    nombre=nombre,
                    defaults={'categoria': cat, 'precio': Decimal(precio), 'stock': stock, 'pub_date': ahora},
                )

        for grupo_nombre, codenames in modulo('roles').PERMISOS.items():
            grupo, _ = Group.objects.get_or_create(name=grupo_nombre)
            permisos = Permission.objects.filter(content_type__app_label='tienda', codename__in=codenames)
            faltan = set(codenames) - set(permisos.values_list('codename', flat=True))
            if faltan:
                self.stdout.write(self.style.WARNING(f'  {grupo_nombre}: no existen los permisos {sorted(faltan)}'))
            grupo.permissions.set(permisos)
            self.stdout.write(f'  {grupo_nombre}: {sorted(permisos.values_list("codename", flat=True))}')

        for usuario, grupo_nombre in USUARIOS:
            u, creado = User.objects.get_or_create(username=usuario, defaults={'is_staff': True})
            if creado:
                u.set_password(clave)
                u.save()
            u.groups.set([Group.objects.get(name=grupo_nombre)])

        self.stdout.write(self.style.SUCCESS(
            f'{Categoria.objects.count()} categorías y {Producto.objects.count()} productos; '
            f'usuarios asistente_ia ({GRUPO_AGENTE}) y revisor ({GRUPO_REVISORES}).'
        ))
