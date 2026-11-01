"""Datos comunes de las pruebas. NO edites las pruebas: son el oráculo del laboratorio."""

import json
from decimal import Decimal, InvalidOperation
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from tienda.management.commands.cargar_sugerencias import ARCHIVO
from tienda.models import Producto, Sugerencia
from tienda.version import modulo

CLAVE = 'clave-de-prueba-1'
INYECCION = 'INSTRUCCIÓN DEL SISTEMA'


def correr(comando, *args):
    salida = StringIO()
    call_command(comando, *args, stdout=salida)
    return salida.getvalue()


def cargar_directo():
    """Mete las 7 sugerencias de forma correcta SIN pasar por validar_forma().

    Así las partes 2 y 3 no dependen de la Parte 1b. La Parte 1b se prueba aparte.
    """
    agente = User.objects.get(username='asistente_ia')
    for item in json.loads(ARCHIVO.read_text(encoding='utf-8')):
        producto = Producto.objects.filter(nombre=item['producto']).first()
        try:
            valor = Decimal(item['valor'])
        except InvalidOperation:
            continue
        if producto:
            Sugerencia.objects.create(producto=producto, campo=item['campo'], valor_propuesto=valor,
                                      motivo=item['motivo'], origen='ia', creado_por=agente)


class TiendaTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        correr('preparar_tienda', '--clave', CLAVE)
        cargar_directo()
        cls.admin = User.objects.create_superuser('admin', 'admin@example.com', CLAVE)
        cls.agente = User.objects.get(username='asistente_ia')
        cls.revisor = User.objects.get(username='revisor')

    @staticmethod
    def verificar(sugerencia):
        return modulo('verificador').verificar(sugerencia)

    def sug(self, producto, campo):
        return Sugerencia.objects.get(producto__nombre=producto, campo=campo)

    def producto(self, nombre):
        return Producto.objects.get(nombre=nombre)

    def accion(self, usuario, accion, sugerencias):
        self.client.force_login(usuario)
        return self.client.post(reverse('admin:tienda_sugerencia_changelist'), {
            'action': accion,
            '_selected_action': [s.pk for s in sugerencias],
        }, follow=True)
