from django.contrib import admin

from .models import Categoria, Producto, Sugerencia
from .version import modulo

admin.site.site_header = 'Tienda · Bandeja del revisor'
admin.site.site_title = 'Bandeja del revisor'
admin.site.index_title = 'Panel de la tienda'


# Categoria y Producto, como en el Lab 5 regular. Ya están hechos.

class ProductoInline(admin.TabularInline):
    model = Producto
    extra = 0
    fields = ('nombre', 'precio', 'stock')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pub_date')
    search_fields = ('nombre',)
    inlines = [ProductoInline]


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock')
    list_filter = ('categoria',)
    search_fields = ('nombre', 'categoria__nombre')
    list_select_related = ('categoria',)


# La bandeja de sugerencias sale de la versión activa (ver version.py):
# la tuya está en tienda/alumno/bandeja.py.
admin.site.register(Sugerencia, modulo('bandeja').SugerenciaAdmin)
