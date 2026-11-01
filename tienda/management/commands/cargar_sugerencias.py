"""Mete en la base las respuestas del asistente de IA (tienda/datos/sugerencias_ia.json).

Solo entran las que pasan validar_forma() (Parte 1b), y entran como PENDIENTES: si se aplican
o no lo decide una persona en la bandeja. Se puede repetir: no duplica.

Las respuestas están escritas a mano imitando fallos típicos de un modelo, no salen de uno real.
"""

import json
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from tienda.models import Sugerencia
from tienda.version import modulo

ARCHIVO = Path(__file__).resolve().parents[2] / 'datos' / 'sugerencias_ia.json'


class Command(BaseCommand):
    help = 'Carga las sugerencias del asistente de IA como pendientes.'

    def add_arguments(self, parser):
        parser.add_argument('--archivo', type=Path, default=ARCHIVO)

    def handle(self, *args, archivo, **options):
        validar_forma = modulo('verificador').validar_forma
        items = json.loads(Path(archivo).read_text(encoding='utf-8'))
        agente = User.objects.filter(username='asistente_ia').first()
        nuevas = repetidas = 0
        for n, item in enumerate(items, start=1):
            try:
                producto, valor = validar_forma(item)
            except ValueError as e:
                self.stdout.write(self.style.WARNING(f'  #{n} no entra: {e}'))
                continue
            except NotImplementedError as e:
                raise CommandError(str(e)) from None
            _, creada = Sugerencia.objects.get_or_create(
                producto=producto, campo=item['campo'], valor_propuesto=valor, motivo=item['motivo'],
                defaults={'origen': 'ia', 'creado_por': agente},
            )
            nuevas += creada
            repetidas += not creada

        self.stdout.write(self.style.SUCCESS(
            f'{nuevas} sugerencia(s) nueva(s) pendiente(s), {repetidas} ya estaba(n). '
            'Revísalas en /admin/tienda/sugerencia/.'
        ))
