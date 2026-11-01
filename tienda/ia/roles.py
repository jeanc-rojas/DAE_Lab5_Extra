"""Versión escrita por un asistente de IA a partir del enunciado del laboratorio.

No edites este archivo: es el punto de partida del duelo (Parte 4). Para corregirlo,
copia la carpeta con `python manage.py duelo --iniciar-corregida` y edita tienda/corregida/.
"""

from tienda.grupos import GRUPO_AGENTE, GRUPO_REVISORES

PERMISOS = {
    GRUPO_AGENTE: [
        'view_producto',
        'add_sugerencia', 'view_sugerencia',
    ],
    GRUPO_REVISORES: [
        'view_categoria', 'view_producto', 'change_producto',
        'view_sugerencia', 'change_sugerencia', 'aprobar_sugerencia',
    ],
}
