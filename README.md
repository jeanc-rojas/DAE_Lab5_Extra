# Lab extra S05 — La bandeja del revisor: la IA propone, el admin decide

La tienda del Lab 5 (categorías y productos) tiene un **asistente de IA** que sugiere cambios de precio y de
stock. El asistente **no toca los productos**: deja sugerencias pendientes. Tú construyes las tres piezas que
deciden qué se aplica:

1. un **verificador** de reglas del negocio (Parte 1);
2. la **bandeja del revisor** en el admin, con la acción «Aprobar y aplicar» (Parte 2);
3. la **frontera del agente**: un usuario para la IA con los permisos mínimos (Parte 3).

Luego corres las mismas pruebas contra una versión que **escribió un asistente de IA**, encuentras sus cuatro
fallos y los corriges (Parte 4). La guía de laboratorio tiene el paso a paso.

## Empezar

```powershell
python -m venv myvenv
myvenv\Scripts\activate
pip install django
python manage.py migrate
python manage.py preparar_tienda       # catálogo, grupos y usuarios asistente_ia / revisor (clave Tecsup2019)
python manage.py createsuperuser
python manage.py duelo                 # casi todo en rojo: es lo esperado
```

## Comandos

| Comando | Para qué |
|---|---|
| `python manage.py duelo` | Corre las pruebas contra **tu** versión (`tienda/alumno/`) y resume por parte |
| `python manage.py duelo --detalle` | Además, el error de cada prueba en rojo |
| `python manage.py cargar_sugerencias` | Mete las respuestas del asistente (necesita la Parte 1b) |
| `python manage.py preparar_tienda` | Repítelo cada vez que cambies `roles.py` |
| `python manage.py duelo ia` | Las mismas pruebas contra la versión de la IA (Parte 4) |
| `python manage.py duelo --iniciar-corregida` | Copia `tienda/ia/` a `tienda/corregida/` para corregirla |
| `python manage.py duelo corregida` | Las pruebas contra tu copia corregida |
| `python manage.py runserver` | El admin en `http://localhost:8000/admin/` con tu versión |

Para ver en el navegador otra versión (por ejemplo la de la IA), en PowerShell:
`$env:TIENDA_VERSION = "ia"; python manage.py runserver` (y `Remove-Item Env:TIENDA_VERSION` para volver a la tuya).

## Estructura

| Carpeta o archivo | Qué es | ¿Lo editas? |
|---|---|---|
| `tienda/alumno/` | **Tu versión**: `verificador.py` (Parte 1), `bandeja.py` (partes 2 y 3b), `roles.py` (Parte 3a) | Sí |
| `tienda/ia/` | La versión que escribió un asistente de IA | **No** |
| `tienda/corregida/` | Tu copia de la de la IA, con los fallos arreglados (la crea `duelo --iniciar-corregida`) | Sí (Parte 4) |
| `tienda/tests/` | Las pruebas: el oráculo del laboratorio | **No** |
| `tienda/datos/sugerencias_ia.json` | Las 9 respuestas del asistente | No |
| `tienda/models.py`, `admin.py`, `version.py`, `management/` | La tienda y los comandos, ya hechos | No |

Las respuestas del asistente y la versión de `tienda/ia/` están **escritas a mano** imitando fallos típicos de
un modelo; no salen de un modelo concreto.

## Entregar

El repositorio en tu GitHub (sin `myvenv/` ni `db.sqlite3`: el `.gitignore` ya los excluye) y el informe con
las tablas y capturas en el campus virtual, como **segunda entrega de laboratorio de la semana 5**.
