"""PARTE 3a — Qué puede hacer cada grupo.

`python manage.py preparar_tienda` crea los dos grupos con estos permisos y les asigna los
usuarios `asistente_ia` (grupo Agente IA) y `revisor` (grupo Revisores).

Cada modelo trae cuatro permisos: add_<modelo>, change_<modelo>, delete_<modelo> y view_<modelo>
(por ejemplo view_producto). Sugerencia trae además uno propio: aprobar_sugerencia.

Después de cambiar esta lista, vuelve a correr `python manage.py preparar_tienda`.
"""

from tienda.grupos import GRUPO_AGENTE, GRUPO_REVISORES

PERMISOS = {
    # TODO(alumno) Parte 3a: el asistente de IA tiene que poder entrar a la bandeja, PROPONER
    # sugerencias y mirar los productos. Nada más: ni cambiar productos, ni cambiar, aprobar o
    # borrar sugerencias. Dale el mínimo de permisos que alcance para eso.
    GRUPO_AGENTE: [],

    # El revisor ya está hecho: mira y cambia productos y sugerencias, y puede aprobar.
    GRUPO_REVISORES: [
        'view_categoria', 'view_producto', 'change_producto',
        'view_sugerencia', 'change_sugerencia', 'aprobar_sugerencia',
    ],
}
