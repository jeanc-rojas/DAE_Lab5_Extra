from django.conf import settings
from django.db import models

# Categoria y Producto son los del Lab 5 regular, campo por campo.


class Categoria(models.Model):
    nombre = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    class Meta:
        verbose_name_plural = 'categorías'

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.IntegerField(default=0)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.nombre


class Sugerencia(models.Model):
    """Un cambio que alguien (casi siempre el asistente de IA) propone sobre un producto.

    La sugerencia no toca el producto. Solo lo cambia la acción «Aprobar y aplicar» del
    admin (Parte 2), y solo si el verificador (Parte 1) no encuentra problemas.
    Este archivo ya está completo: no hace falta tocarlo.
    """

    CAMPOS = [('precio', 'precio'), ('stock', 'stock')]
    ORIGENES = [('ia', 'asistente de IA'), ('persona', 'persona')]
    PENDIENTE, APROBADA, RECHAZADA = 'pendiente', 'aprobada', 'rechazada'
    ESTADOS = [(PENDIENTE, 'pendiente'), (APROBADA, 'aprobada'), (RECHAZADA, 'rechazada')]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='sugerencias')
    campo = models.CharField(max_length=10, choices=CAMPOS)
    valor_propuesto = models.DecimalField(max_digits=8, decimal_places=2)
    # El motivo es texto libre que escribió el modelo: se muestra, nunca se obedece.
    motivo = models.TextField()
    origen = models.CharField(max_length=10, choices=ORIGENES, default='ia')
    estado = models.CharField(max_length=10, choices=ESTADOS, default=PENDIENTE)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='sugerencias_creadas',
    )
    creada = models.DateTimeField(auto_now_add=True)
    # Lo que llena la persona que decide (bitácora de la decisión).
    decidido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='sugerencias_decididas',
    )
    decidido_en = models.DateTimeField(null=True, blank=True)
    valor_anterior = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['-creada']
        # Permiso propio: quien no lo tiene no debería ni ver la acción «Aprobar y aplicar».
        permissions = [('aprobar_sugerencia', 'Puede aprobar y aplicar sugerencias')]

    def __str__(self):
        valor = self.valor_propuesto
        if self.campo == 'stock' and valor == valor.to_integral_value():
            valor = int(valor)
        return f'{self.producto} · {self.campo} → {valor}'

    def valor_actual(self):
        return getattr(self.producto, self.campo)
