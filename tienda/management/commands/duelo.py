"""Corre las pruebas contra una versión de la bandeja y resume el resultado por parte.

    python manage.py duelo                      # tu versión (tienda/alumno/)
    python manage.py duelo ia                   # la que escribió el asistente de IA
    python manage.py duelo --iniciar-corregida  # copia tienda/ia/ a tienda/corregida/ (Parte 4)
    python manage.py duelo corregida            # tu copia corregida de la IA
    python manage.py duelo ia --detalle         # además, el error completo de cada prueba que falla

Las pruebas no se tocan: son el oráculo. Lo que cambias es el código de tu versión.
"""

import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from tienda.version import VERSIONES

PARTES = {
    'test_p1_verificador': 'Parte 1 · verificador y carga',
    'test_p2_bandeja': 'Parte 2 · bandeja y acción',
    'test_p3_frontera': 'Parte 3 · frontera del agente',
}
LINEA = re.compile(r'^(test_\w+) \(tienda\.tests\.(test_p\d_\w+)\.(\w+)\.\w+\) \.\.\. (ok|FAIL|ERROR)', re.M)
TIENDA = Path(__file__).resolve().parents[2]


class Command(BaseCommand):
    help = 'Corre las pruebas contra una versión (alumno, ia, corregida) y resume por parte.'

    def add_arguments(self, parser):
        parser.add_argument('version', nargs='?', default='alumno', choices=list(VERSIONES))
        parser.add_argument('--detalle', action='store_true', help='muestra el error completo de las pruebas en rojo')
        parser.add_argument('--iniciar-corregida', action='store_true', help='copia tienda/ia/ a tienda/corregida/')
        parser.add_argument('--forzar', action='store_true', help='con --iniciar-corregida: pisa la copia que haya')

    def handle(self, *args, version, detalle, iniciar_corregida, forzar, **options):
        # En Windows, si la salida va a un archivo, la consola puede no saber escribir ✔ o ✘.
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(errors='backslashreplace')
        if iniciar_corregida:
            return self.iniciar_corregida(forzar)

        entorno = {**os.environ, 'TIENDA_VERSION': version, 'PYTHONIOENCODING': 'utf-8'}
        proceso = subprocess.run(
            [sys.executable, 'manage.py', 'test', 'tienda.tests', '-v', '2', '--noinput'],
            cwd=settings.BASE_DIR, env=entorno, capture_output=True, text=True, encoding='utf-8',
        )
        salida = proceso.stdout + proceso.stderr
        resultados = LINEA.findall(salida)
        if not resultados:
            self.stdout.write(salida[-3000:])
            raise CommandError(f'Las pruebas no llegaron a correr con la versión «{version}» (mira el error de arriba).')

        por_parte = defaultdict(list)
        for prueba, modulo, _clase, estado in resultados:
            por_parte[modulo].append((prueba, estado))

        self.stdout.write(f'\nVersión: {version}  ({VERSIONES[version].replace(".", "/")}/)\n')
        total = verdes = 0
        for modulo, titulo in PARTES.items():
            pruebas = por_parte.get(modulo, [])
            ok = sum(estado == 'ok' for _, estado in pruebas)
            total, verdes = total + len(pruebas), verdes + ok
            estilo = self.style.SUCCESS if ok == len(pruebas) else self.style.ERROR
            self.stdout.write(estilo(f'{titulo:34} {ok:2} de {len(pruebas):2} en verde'))
            for prueba, estado in pruebas:
                if estado != 'ok':
                    self.stdout.write(f'    - {prueba} ({estado})')

        self.stdout.write('')
        if verdes == total:
            self.stdout.write(self.style.SUCCESS(f'Todo en verde: {verdes} de {total}.'))
        else:
            self.stdout.write(self.style.WARNING(f'{total - verdes} en rojo de {total}.'))
            if detalle:
                self.stdout.write(self.detalle(salida))
            else:
                comando = 'python manage.py duelo' + ('' if version == 'alumno' else f' {version}') + ' --detalle'
                self.stdout.write(f'Para ver por qué falla cada una: {comando}')
            sys.exit(1)

    def detalle(self, salida):
        bloques = salida.split('=' * 70)
        return '\n'.join('=' * 70 + b.split('-' * 70 + '\nRan')[0] for b in bloques[1:])

    def iniciar_corregida(self, forzar):
        destino = TIENDA / 'corregida'
        if destino.exists() and not forzar:
            raise CommandError('tienda/corregida/ ya existe. Para empezar de nuevo desde la IA: --iniciar-corregida --forzar')
        if destino.exists():
            shutil.rmtree(destino)
        shutil.copytree(TIENDA / 'ia', destino, ignore=shutil.ignore_patterns('__pycache__'))
        self.stdout.write(self.style.SUCCESS(
            'Copiado tienda/ia/ → tienda/corregida/. Edita SOLO tienda/corregida/ y comprueba con: '
            'python manage.py duelo corregida'
        ))
