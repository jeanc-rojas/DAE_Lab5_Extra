"""Versión escrita por un asistente de IA a partir del enunciado del laboratorio.

No edites este archivo: es el punto de partida del duelo (Parte 4). Para corregirlo,
copia la carpeta con `python manage.py duelo --iniciar-corregida` y edita tienda/corregida/.
"""

from django.contrib import admin, messages
from django.db import transaction
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import Truncator

from tienda.grupos import es_agente
from tienda.models import Sugerencia

from .verificador import verificar


class SugerenciaAdmin(admin.ModelAdmin):
    list_display = (
        'producto', 'campo', 'valor_actual_col', 'valor_propuesto', 'verificacion',
        'motivo_corto', 'origen', 'estado', 'creado_por',
    )
    list_filter = ('estado', 'origen', 'campo')
    search_fields = ('producto__nombre', 'motivo')
    list_select_related = ('producto', 'creado_por')
    actions = ['aprobar_y_aplicar', 'rechazar']

    def get_readonly_fields(self, request, obj=None):
        siempre = ['origen', 'estado', 'creado_por', 'decidido_por', 'decidido_en', 'valor_anterior']
        if obj is None:
            return siempre
        return ['producto', 'campo', 'valor_propuesto', 'motivo'] + siempre

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
            obj.origen = 'ia' if es_agente(request.user) else 'persona'
        super().save_model(request, obj, form, change)

    @admin.display(description='actual')
    def valor_actual_col(self, obj):
        return obj.valor_actual()

    @admin.display(description='verificador')
    def verificacion(self, obj):
        if obj.estado != Sugerencia.PENDIENTE:
            return '—'
        problemas = verificar(obj)
        return '✘ ' + '; '.join(problemas) if problemas else '✔ pasa'

    @admin.display(description='motivo')
    def motivo_corto(self, obj):
        # mark_safe para conservar el formato del motivo (negritas, saltos de línea).
        return mark_safe(Truncator(obj.motivo).chars(60))

    @admin.action(description='Aprobar y aplicar (solo las que pasan el verificador)')
    def aprobar_y_aplicar(self, request, queryset):
        aplicadas, bloqueadas = 0, []
        with transaction.atomic():
            for s in queryset.select_related('producto'):
                problemas = verificar(s)
                if problemas:
                    bloqueadas.append(f'«{s}»: {"; ".join(problemas)}')
                    continue
                producto = s.producto
                s.valor_anterior = getattr(producto, s.campo)
                nuevo = int(s.valor_propuesto) if s.campo == 'stock' else s.valor_propuesto
                setattr(producto, s.campo, nuevo)
                producto.save(update_fields=[s.campo])
                s.estado = Sugerencia.APROBADA
                s.decidido_por = request.user
                s.decidido_en = timezone.now()
                s.save()
                self.log_change(request, producto, f'{s.campo}: {s.valor_anterior} → {nuevo} (sugerencia #{s.pk})')
                self.log_change(request, s, 'Aprobada y aplicada')
                aplicadas += 1

        if aplicadas:
            self.message_user(request, f'{aplicadas} sugerencia(s) aplicada(s).', messages.SUCCESS)
        for texto in bloqueadas:
            self.message_user(request, f'No se aplicó {texto}. Sigue pendiente.', messages.WARNING)

    @admin.action(description='Rechazar', permissions=['change'])
    def rechazar(self, request, queryset):
        n = 0
        for s in queryset.filter(estado=Sugerencia.PENDIENTE):
            s.estado = Sugerencia.RECHAZADA
            s.decidido_por = request.user
            s.decidido_en = timezone.now()
            s.save()
            self.log_change(request, s, 'Rechazada')
            n += 1
        self.message_user(request, f'{n} sugerencia(s) rechazada(s).', messages.SUCCESS)
