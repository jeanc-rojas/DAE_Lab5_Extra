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
    valor = sugerencia.valor_propuesto
    problemas = []

    if sugerencia.campo == 'precio':
        actual = sugerencia.producto.precio
        if valor <= 0:
            problemas.append('el precio tiene que ser mayor que 0')
        elif abs(valor - actual) > actual * VARIACION_MAXIMA_PRECIO:
            problemas.append(f'el precio se aleja más de ±30 % del actual ({actual})')
    elif sugerencia.campo == 'stock':
        if valor != valor.to_integral_value():
            problemas.append('el stock tiene que ser un número entero')
        elif valor < 0:
            problemas.append('el stock no puede ser negativo')
        elif valor > STOCK_MAXIMO:
            problemas.append(f'el stock no puede pasar de {STOCK_MAXIMO}')
    else:
        problemas.append(f'campo desconocido: {sugerencia.campo}')

    return problemas


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
    if not isinstance(item, dict):
        raise ValueError('la sugerencia no es un diccionario')

    faltan = CLAVES - item.keys()
    if faltan:
        raise ValueError(f'le faltan claves: {", ".join(sorted(faltan))}')

    nombre = item['producto']
    if not isinstance(nombre, str):
        raise ValueError(f'el producto «{nombre}» no existe en el catálogo')
    producto = Producto.objects.filter(nombre__iexact=nombre).first()
    if producto is None:
        raise ValueError(f'el producto «{nombre}» no existe en el catálogo')

    campo = item['campo']
    if not isinstance(campo, str) or campo not in {c for c, _ in Sugerencia.CAMPOS}:
        raise ValueError(f'campo desconocido «{campo}»')

    valor_texto = item['valor']
    try:
        valor = Decimal(str(valor_texto))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f'el valor «{valor_texto}» no es un número') from None
    if not valor.is_finite():
        raise ValueError(f'el valor «{valor_texto}» no es un número')

    return producto, valor
