"""Interfaz de linea de comandos del prototipo.

Uso:
    python -m src.cli                         # sesion interactiva
    python -m src.cli --consulta "..."        # una sola consulta
    python -m src.cli --usuario u-004 --controles
"""
from __future__ import annotations

import argparse
import sys

from . import config
from .asistente import Asistente, Controles
from .registro import Registro


def _argumentos() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Mesa de ayuda interna de TI (prototipo)")
    p.add_argument("--consulta", help="consulta unica; sin esto arranca el modo interactivo")
    p.add_argument("--usuario", default="u-001", help="identificador del usuario sintetico (u-001 a u-004)")
    p.add_argument("--proveedor", default=None, help="gemini o eco; por defecto, el de config")
    p.add_argument("--controles", action="store_true", help="activa los tres controles")
    p.add_argument("--corrida", default=None, help="nombre del archivo de registro")
    return p.parse_args()


def _imprimir(respuesta, asistente: Asistente) -> None:
    print()
    print(respuesta.texto)
    print()
    if respuesta.documentos:
        citas = ", ".join(f"{d['id']} ({d['clasificacion']})" for d in respuesta.documentos)
        print(f"  documentos recuperados: {citas}")
    else:
        print("  documentos recuperados: ninguno")
    for inv in respuesta.herramientas:
        estado = "ejecutada" if inv["permitida"] else "bloqueada"
        print(f"  herramienta {inv['herramienta']}: {estado}")
    print(f"  registro: {asistente.registro.ruta}")
    print()


def main() -> int:
    args = _argumentos()
    controles = Controles(True, True, True) if args.controles else Controles()
    registro = Registro(args.corrida)
    asistente = Asistente(registro=registro, controles=controles, proveedor=args.proveedor)

    estado = "activados" if args.controles else "desactivados (linea base)"
    usuario = asistente.usuarios.get(args.usuario, {})
    print(f"Mesa de ayuda interna de TI · {config.ORGANIZACION} (ficticia)")
    print(f"  modelo: {asistente.modelo.proveedor}/{asistente.modelo.nombre}")
    print(f"  usuario: {args.usuario} · {usuario.get('nombre', '?')} · rol {usuario.get('rol', '?')}")
    print(f"  controles: {estado}")
    print(f"  corpus: {len(asistente.documentos)} documentos sinteticos")

    if args.consulta:
        _imprimir(asistente.responder(args.consulta, id_usuario=args.usuario), asistente)
        return 0

    print("\nEscribe tu consulta. Linea vacia o Ctrl+D para salir.\n")
    while True:
        try:
            consulta = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not consulta:
            return 0
        _imprimir(asistente.responder(consulta, id_usuario=args.usuario), asistente)


if __name__ == "__main__":
    sys.exit(main())
