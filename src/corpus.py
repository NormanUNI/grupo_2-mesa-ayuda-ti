"""Carga del corpus documental sintetico."""
from __future__ import annotations

import pathlib
from typing import Any

from . import config


def _leer_frontmatter(texto: str) -> tuple[dict[str, str], str]:
    if not texto.startswith("---"):
        return {}, texto
    cierre = texto.find("\n---", 3)
    if cierre == -1:
        return {}, texto
    cabecera = texto[3:cierre].strip()
    cuerpo = texto[cierre + 4 :].lstrip("\n")
    meta: dict[str, str] = {}
    for linea in cabecera.splitlines():
        if ":" in linea:
            clave, _, valor = linea.partition(":")
            meta[clave.strip()] = valor.strip()
    return meta, cuerpo


def cargar(directorio: pathlib.Path | None = None) -> list[dict[str, Any]]:
    """Devuelve la lista de documentos del corpus, ordenada por identificador."""
    directorio = directorio or config.DIR_CORPUS
    documentos: list[dict[str, Any]] = []
    for ruta in sorted(directorio.glob("*.md")):
        meta, cuerpo = _leer_frontmatter(ruta.read_text(encoding="utf-8"))
        documentos.append(
            {
                "id": meta.get("id", ruta.stem),
                "titulo": meta.get("titulo", ruta.stem),
                "area": meta.get("area", "Sin area"),
                "clasificacion": meta.get("clasificacion", "interno"),
                "origen": meta.get("origen", "sintetico"),
                "archivo": ruta.name,
                "texto": cuerpo.strip(),
            }
        )
    return documentos
