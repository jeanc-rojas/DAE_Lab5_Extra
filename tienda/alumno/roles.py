"""PARTE 3a — Qué puede hacer cada grupo.

`python manage.py preparar_tienda` crea los dos grupos con estos permisos y les asigna los
usuarios `asistente_ia` (grupo Agente IA) y `revisor` (grupo Revisores).

Cada modelo trae cuatro permisos: add_<modelo>, change_<modelo>, delete_<modelo> y view_<modelo>
(por ejemplo view_producto). Sugerencia trae además uno propio: aprobar_sugerencia.

Después de cambiar esta lista, vuelve a correr `python manage.py preparar_tienda`.
"""

from tienda.grupos import GRUPO_AGENTE, GRUPO_REVISORES

PERMISOS = {
    GRUPO_AGENTE: [
        'view_producto', 'view_sugerencia', 'add_sugerencia',
    ],

    # El revisor ya está hecho: mira y cambia productos y sugerencias, y puede aprobar.
    GRUPO_REVISORES: [
        'view_categoria', 'view_producto', 'change_producto',
        'view_sugerencia', 'change_sugerencia', 'aprobar_sugerencia',
    ],
}
