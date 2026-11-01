"""Los nombres de los dos grupos del laboratorio. Los permisos de cada uno están en roles.py (Parte 3)."""

GRUPO_AGENTE = 'Agente IA'
GRUPO_REVISORES = 'Revisores'


def es_agente(usuario):
    return usuario.groups.filter(name=GRUPO_AGENTE).exists()
