"""Versión escrita por un asistente de IA a partir del enunciado del laboratorio.

No edites este archivo: es el punto de partida del duelo (Parte 4). Para corregirlo,
copia la carpeta con `python manage.py duelo --iniciar-corregida` y edita tienda/corregida/.
"""

from decimal import Decimal, InvalidOperation

from tienda.models import Producto, Sugerencia

VARIACION_MAXIMA_PRECIO = Decimal('0.30')
STOCK_MAXIMO = 999
CLAVES = {'producto', 'campo', 'valor', 'motivo'}


def verificar(sugerencia):
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
    if not isinstance(item, dict) or not CLAVES <= item.keys():
        raise ValueError('le faltan claves (producto, campo, valor, motivo)')
    producto = Producto.objects.filter(nombre__iexact=item['producto']).first()
    if producto is None:
        raise ValueError(f'el producto «{item["producto"]}» no existe en el catálogo')
    if item['campo'] not in {c for c, _ in Sugerencia.CAMPOS}:
        raise ValueError(f'campo desconocido «{item["campo"]}»')
    try:
        valor = Decimal(str(item['valor']))
    except InvalidOperation:
        raise ValueError(f'el valor «{item["valor"]}» no es un número') from None
    if not valor.is_finite():
        raise ValueError(f'el valor «{item["valor"]}» no es un número')
    return producto, valor
