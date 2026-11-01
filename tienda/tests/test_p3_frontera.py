"""Parte 3 — La frontera del agente: permisos (3a), permiso propio de la acción y quién crea (3b)."""

from decimal import Decimal

from django.urls import reverse

from tienda.grupos import GRUPO_AGENTE
from tienda.models import Sugerencia

from .base import TiendaTestCase

LISTA = reverse('admin:tienda_sugerencia_changelist')


class FronteraTests(TiendaTestCase):
    def test_permisos_minimos_del_agente(self):
        permisos = set(self.agente.get_all_permissions())
        for necesario in ('tienda.add_sugerencia', 'tienda.view_sugerencia', 'tienda.view_producto'):
            self.assertIn(necesario, permisos)
        for prohibido in ('tienda.change_producto', 'tienda.change_sugerencia', 'tienda.aprobar_sugerencia',
                          'tienda.delete_producto', 'tienda.delete_sugerencia', 'tienda.add_producto'):
            self.assertNotIn(prohibido, permisos)
        self.assertTrue(self.agente.groups.filter(name=GRUPO_AGENTE).exists())

    def test_el_agente_entra_a_la_bandeja(self):
        self.client.force_login(self.agente)
        r = self.client.get(LISTA)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Seleccione sugerencia para ver')

    def test_el_agente_no_puede_aprobar(self):
        self.client.force_login(self.agente)
        self.assertNotContains(self.client.get(LISTA), 'value="aprobar_y_aplicar"',
                               msg_prefix='el agente ve la acción «Aprobar y aplicar»')
        self.accion(self.agente, 'aprobar_y_aplicar', [self.sug('Fanta', 'stock')])  # y si la fuerza…
        self.assertEqual(self.producto('Fanta').stock, 0)
        self.assertEqual(self.sug('Fanta', 'stock').estado, 'pendiente')

    def test_el_agente_no_cambia_productos(self):
        self.client.force_login(self.agente)
        fanta = self.producto('Fanta')
        url = reverse('admin:tienda_producto_change', args=[fanta.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        r = self.client.post(url, {'categoria': fanta.categoria_id, 'nombre': 'Fanta', 'precio': '0.10',
                                   'stock': '999', 'pub_date_0': '2026-10-26', 'pub_date_1': '10:00:00'})
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.producto('Fanta').precio, Decimal('1.80'))

    def test_lo_que_propone_el_agente_queda_a_su_nombre(self):
        self.client.force_login(self.agente)
        self.client.post(reverse('admin:tienda_sugerencia_add'), {
            'producto': self.producto('Fanta').pk, 'campo': 'stock', 'valor_propuesto': '24',
            'motivo': 'Reponer', 'estado': 'aprobada', 'origen': 'persona',
        })
        s = Sugerencia.objects.get(motivo='Reponer')
        self.assertEqual((s.estado, s.origen, s.creado_por), ('pendiente', 'ia', self.agente))
        self.assertEqual(self.producto('Fanta').stock, 0)

    def test_lo_que_propone_una_persona_queda_como_persona(self):
        self.client.force_login(self.admin)
        self.client.post(reverse('admin:tienda_sugerencia_add'), {
            'producto': self.producto('Oreo').pk, 'campo': 'stock', 'valor_propuesto': '60', 'motivo': 'Inventario',
        })
        s = Sugerencia.objects.get(motivo='Inventario')
        self.assertEqual((s.origen, s.creado_por), ('persona', self.admin))

    def test_el_revisor_si_aprueba(self):
        self.client.force_login(self.revisor)
        self.assertContains(self.client.get(LISTA), 'value="aprobar_y_aplicar"')
        self.accion(self.revisor, 'aprobar_y_aplicar', [self.sug('Coca-Cola', 'precio')])
        self.assertEqual(self.producto('Coca-Cola').precio, Decimal('2.70'))
