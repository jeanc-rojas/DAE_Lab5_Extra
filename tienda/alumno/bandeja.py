"""PARTES 2 y 3b — La bandeja del revisor: el ModelAdmin de Sugerencia.

Lo que ya está hecho te sirve de modelo: la columna «actual», la acción «Rechazar» (mírala
antes de escribir «Aprobar y aplicar») y la regla de que las sugerencias no se borran.

Comprueba tu avance con: python manage.py duelo
"""

from django.contrib import admin, messages  # noqa: F401
from django.db import transaction  # noqa: F401
from django.utils import timezone
from django.utils.text import Truncator  # noqa: F401

from tienda.grupos import es_agente  # noqa: F401
from tienda.models import Sugerencia

from .verificador import verificar  # noqa: F401


class SugerenciaAdmin(admin.ModelAdmin):
    # TODO(alumno) Parte 2a: la lista de la bandeja.
    # - list_display con: producto, campo, valor actual ('valor_actual_col'), valor propuesto,
    #   el veredicto del verificador ('verificacion'), el motivo ('motivo_corto'), origen, estado
    #   y creado_por.
    # - list_filter por estado, origen y campo; search_fields por nombre del producto y motivo.
    list_display = ('__str__', 'estado')
    list_select_related = ('producto', 'creado_por')
    actions = ['aprobar_y_aplicar', 'rechazar']

    # TODO(alumno) Parte 2b: qué no se puede escribir a mano.
    # - Al crear (obj is None): origen, estado, creado_por y los tres campos de la decisión.
    #   El estado solo lo cambian las acciones; nadie nace «aprobada».
    # - Al editar (obj existe): además producto, campo, valor_propuesto y motivo. La propuesta
    #   se aprueba o se rechaza tal como vino; no se retoca.
    def get_readonly_fields(self, request, obj=None):
        return ['decidido_por', 'decidido_en', 'valor_anterior']

    # Las sugerencias son la bitácora de lo que propuso la IA y de quién lo decidió: no se borran.
    def has_delete_permission(self, request, obj=None):
        return False

    # TODO(alumno) Parte 3b: al CREAR una sugerencia desde el admin, guarda quién la creó
    # (request.user) y su origen: 'ia' si el usuario es del grupo del agente (es_agente),
    # 'persona' si no. Luego llama a super().save_model(...).
    # def save_model(self, request, obj, form, change):

    @admin.display(description='actual')
    def valor_actual_col(self, obj):
        return obj.valor_actual()

    # TODO(alumno) Parte 2a: la columna del verificador.
    # '—' si la sugerencia ya no está pendiente; si lo está, '✔ pasa' o '✘ ' seguido de los
    # problemas que devuelve verificar(), separados por '; '.
    @admin.display(description='verificador')
    def verificacion(self, obj):
        raise NotImplementedError('TODO(alumno) Parte 2a: columna verificacion')

    # TODO(alumno) Parte 2a: el motivo, recortado a 60 caracteres (Truncator(texto).chars(60)).
    # Ojo: uno de los motivos trae HTML. Tiene que verse como texto en la bandeja.
    @admin.display(description='motivo')
    def motivo_corto(self, obj):
        raise NotImplementedError('TODO(alumno) Parte 2a: columna motivo_corto')

    # TODO(alumno) Parte 3b: que solo quien tenga el permiso propio 'tienda.aprobar_sugerencia'
    # vea y pueda ejecutar esta acción. Se hace con permissions=['aprobar'] en el decorador y un
    # método has_aprobar_permission(self, request) que devuelva True o False.
    @admin.action(description='Aprobar y aplicar (solo las que pasan el verificador)')
    def aprobar_y_aplicar(self, request, queryset):
        """TODO(alumno) Parte 2c. Para cada sugerencia elegida:

        1. Si ya no está pendiente, NO se toca (cuéntala: al final se avisa «ya estaba(n) decidida(s)»).
        2. Si verificar() devuelve problemas, NO se aplica: sigue pendiente y se avisa por qué
           (messages.WARNING, un mensaje por sugerencia que diga «No se aplicó …»).
        3. Si pasa: guarda el valor anterior en valor_anterior, cambia el campo del producto
           (el stock como int), marca la sugerencia como aprobada con decidido_por y decidido_en, y
           deja rastro en el Historial con self.log_change(request, producto, 'precio: 2.50 → 2.70 …').
        Al final: «N sugerencia(s) aplicada(s).» con messages.SUCCESS.
        Hazlo dentro de `with transaction.atomic():` para que se aplique todo o nada.
        """
        raise NotImplementedError('TODO(alumno) Parte 2c: acción aprobar_y_aplicar')

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
