"""Parte 2 — La bandeja (2a, 2b) y la acción «Aprobar y aplicar» (2c), usadas por el superusuario."""

from decimal import Decimal

from django.contrib.admin.models import LogEntry
from django.urls import reverse

from tienda.models import Producto, Sugerencia

from .base import INYECCION, TiendaTestCase

LISTA = reverse('admin:tienda_sugerencia_changelist')


class BandejaTests(TiendaTestCase):
    def setUp(self):
        self.client.force_login(self.admin)

    def test_columnas_filtros_y_busqueda(self):
        r = self.client.get(LISTA)
        self.assertEqual(r.status_code, 200)
        for columna in ('column-valor_actual_col', 'column-verificacion', 'column-motivo_corto',
                        'column-origen', 'column-creado_por'):
            self.assertContains(r, columna)
        self.assertContains(r, '?estado__exact=pendiente')
        self.assertContains(r, '?origen__exact=ia')
        self.assertContains(r, '?campo__exact=stock')
        r = self.client.get(LISTA, {'q': 'vencidos'})  # busca en el motivo
        self.assertContains(r, '1 sugerencia')

    def test_veredicto_del_verificador_en_la_lista(self):
        r = self.client.get(LISTA)
        self.assertContains(r, '✔ pasa')
        self.assertContains(r, '✘ el precio tiene que ser mayor que 0')
        self.assertContains(r, '✘ el stock no puede ser negativo')

    def test_el_html_del_motivo_se_muestra_como_texto(self):
        r = self.client.get(LISTA)
        self.assertContains(r, '&lt;img src=x onerror=')
        self.assertNotContains(r, '<img src=x')

    def test_nadie_nace_aprobada(self):
        self.client.post(reverse('admin:tienda_sugerencia_add'), {
            'producto': self.producto('Fanta').pk, 'campo': 'stock', 'valor_propuesto': '24',
            'motivo': 'A mano', 'origen': 'persona', 'estado': 'aprobada', 'decidido_por': self.admin.pk,
        })
        s = Sugerencia.objects.get(motivo='A mano')
        self.assertEqual((s.estado, s.decidido_por), ('pendiente', None))

    def test_la_propuesta_no_se_retoca(self):
        oreo = self.sug('Oreo', 'stock')
        r = self.client.get(reverse('admin:tienda_sugerencia_change', args=[oreo.pk]))
        self.assertEqual(r.status_code, 200)
        self.client.post(reverse('admin:tienda_sugerencia_change', args=[oreo.pk]), {
            'producto': oreo.producto_id, 'campo': 'stock', 'valor_propuesto': '10', 'motivo': 'retocado',
            'origen': 'ia', 'estado': 'aprobada',
        })
        oreo.refresh_from_db()
        self.assertEqual((oreo.valor_propuesto, oreo.estado), (Decimal('-10'), 'pendiente'))
        self.assertNotEqual(oreo.motivo, 'retocado')


class AprobarTests(TiendaTestCase):
    def sin_inyeccion(self):
        # La sugerencia con órdenes en el motivo se prueba en la Parte 1.
        return Sugerencia.objects.exclude(motivo__contains=INYECCION)

    def test_aplica_solo_las_que_pasan(self):
        r = self.accion(self.admin, 'aprobar_y_aplicar', self.sin_inyeccion())
        self.assertContains(r, '3 sugerencia(s) aplicada(s)')
        self.assertContains(r, 'No se aplicó', count=3)
        self.assertEqual(self.producto('Fanta').stock, 48)
        self.assertEqual(self.producto('Coca-Cola').precio, Decimal('2.70'))
        self.assertEqual(self.producto('Coca-Cola').stock, 36)
        self.assertEqual(self.producto('Inca Kola').precio, Decimal('2.50'))
        self.assertEqual(self.producto('Oreo').stock, 40)
        self.assertEqual(self.producto('Papas Lays').precio, Decimal('1.50'))
        self.assertEqual(Sugerencia.objects.filter(estado='aprobada').count(), 3)

    def test_deja_rastro_de_quien_decidio(self):
        fanta = self.sug('Fanta', 'stock')
        self.accion(self.admin, 'aprobar_y_aplicar', [fanta])
        fanta.refresh_from_db()
        self.assertEqual((fanta.estado, fanta.decidido_por, fanta.valor_anterior), ('aprobada', self.admin, 0))
        self.assertIsNotNone(fanta.decidido_en)
        self.assertTrue(LogEntry.objects.filter(object_repr='Fanta', change_message__contains='0 → 48').exists(),
                        'el Historial de Fanta no dice «0 → 48»')

    def test_aprobar_dos_veces_no_vuelve_a_aplicar(self):
        fanta = self.sug('Fanta', 'stock')
        self.accion(self.admin, 'aprobar_y_aplicar', [fanta])
        Producto.objects.filter(nombre='Fanta').update(stock=5)  # alguien vendió después
        r = self.accion(self.admin, 'aprobar_y_aplicar', [fanta])
        self.assertContains(r, 'ya estaba(n) decidida(s)')
        self.assertEqual(self.producto('Fanta').stock, 5)

    def test_rechazar(self):
        oreo = self.sug('Oreo', 'stock')
        self.accion(self.admin, 'rechazar', [oreo])
        oreo.refresh_from_db()
        self.assertEqual((oreo.estado, oreo.decidido_por), ('rechazada', self.admin))

    def test_las_sugerencias_no_se_borran(self):
        s = Sugerencia.objects.first()
        self.client.force_login(self.admin)
        self.assertNotContains(self.client.get(LISTA), 'value="delete_selected"')
        self.assertEqual(self.client.get(reverse('admin:tienda_sugerencia_delete', args=[s.pk])).status_code, 403)
