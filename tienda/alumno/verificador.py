"""PARTE 1 — Las dos revisiones que hace un programa antes de que una persona mire nada.

1a. `verificar(sugerencia)`: las reglas del negocio. Se usa en la columna «verificador» de la
    bandeja y en la acción «Aprobar y aplicar» (Parte 2).
1b. `validar_forma(item)`: la puerta de entrada. La usa `python manage.py cargar_sugerencias`
    para decidir qué respuestas del asistente entran a la base de datos.

Comprueba tu avance con: python manage.py duelo
"""

from decimal import Decimal, InvalidOperation  # noqa: F401  (los vas a necesitar)

from tienda.models import Producto, Sugerencia  # noqa: F401

VARIACION_MAXIMA_PRECIO = Decimal('0.30')  # ±30 % sobre el precio actual
STOCK_MAXIMO = 999
CLAVES = {'producto', 'campo', 'valor', 'motivo'}


def verificar(sugerencia):
    """Devuelve la lista de problemas de la sugerencia; la lista vacía significa «se puede aplicar».

    Reglas (cada problema es un texto en español; las pruebas buscan las palabras en negrita):
    - precio: tiene que ser **mayor que 0**, y no puede alejarse más de **±30 %** del precio actual
      del producto (`sugerencia.producto.precio`).
    - stock: tiene que ser un número **entero** (sin decimales), **no** puede ser **negativo** y no
      puede pasar de STOCK_MAXIMO (texto: «no puede pasar de 999»).
    - cualquier otro campo: «campo desconocido».

    Mira solo el producto, el campo y el valor (`sugerencia.valor_propuesto`, un Decimal).
    El motivo lo escribió el modelo de IA: es un dato para que lo lea una persona, no una
    instrucción para tu programa.
    """
    raise NotImplementedError('TODO(alumno) Parte 1a: escribe verificar() en tienda/alumno/verificador.py')


def validar_forma(item):
    """Revisa la FORMA de una respuesta del asistente (un dict leído de tienda/datos/sugerencias_ia.json).

    Si está bien, devuelve la tupla (producto, valor): el Producto de la base de datos y el valor como Decimal.
    Si no, lanza ValueError con un mensaje que diga qué falla:
    - le faltan claves (tienen que estar las cuatro de CLAVES)          → «le faltan claves …»
    - el producto no existe (búscalo por nombre sin distinguir mayúsculas) → «… no existe en el catálogo»
    - el campo no es «precio» ni «stock»                               → «campo desconocido …»
    - el valor no se puede convertir a Decimal                          → «… no es un número»

    Pista: Decimal('veinte') lanza InvalidOperation.
    """
    raise NotImplementedError('TODO(alumno) Parte 1b: escribe validar_forma() en tienda/alumno/verificador.py')
