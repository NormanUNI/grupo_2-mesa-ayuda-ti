"""Memoria entre sesiones.

Guarda un historial corto por usuario para dar seguimiento a incidencias previas.
Un archivo JSON por usuario en datos/memoria/.

El aislamiento por usuario es una propiedad que la evaluacion adversarial debe
medir, no asumir: la clase acepta `aislar=False` para reproducir el
comportamiento sin control, en el que la memoria se recupera sin filtrar por
usuario.
"""
from __future__ import annotations

import datetime as _dt
import json
import pathlib
from typing import Any

from . import config

MAXIMO_ENTRADAS = 10


class Memoria:
    def __init__(self, directorio: pathlib.Path | None = None, aislar: bool = True):
        self.directorio = directorio or config.DIR_MEMORIA
        self.directorio.mkdir(parents=True, exist_ok=True)
        self.aislar = aislar

    def _ruta(self, id_usuario: str) -> pathlib.Path:
        seguro = "".join(c for c in id_usuario if c.isalnum() or c in "-_")
        return self.directorio / f"{seguro}.json"

    def recuperar(self, id_usuario: str) -> list[dict[str, Any]]:
        if self.aislar:
            rutas = [self._ruta(id_usuario)]
        else:
            # Sin aislamiento: la memoria de todos los usuarios entra al contexto.
            rutas = sorted(self.directorio.glob("*.json"))
        entradas: list[dict[str, Any]] = []
        for ruta in rutas:
            if ruta.exists():
                entradas.extend(json.loads(ruta.read_text(encoding="utf-8")))
        entradas.sort(key=lambda e: e.get("marca_tiempo", ""))
        return entradas[-MAXIMO_ENTRADAS:]

    def escribir(self, id_usuario: str, resumen: str, id_consulta: str) -> dict[str, Any]:
        ruta = self._ruta(id_usuario)
        entradas = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else []
        entrada = {
            "marca_tiempo": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "id_usuario": id_usuario,
            "id_consulta": id_consulta,
            "resumen": resumen[:300],
        }
        entradas.append(entrada)
        ruta.write_text(
            json.dumps(entradas[-MAXIMO_ENTRADAS:], indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return entrada

    def limpiar(self) -> None:
        for ruta in self.directorio.glob("*.json"):
            ruta.unlink()
