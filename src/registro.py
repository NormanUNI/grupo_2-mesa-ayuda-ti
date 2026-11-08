"""Registro de eventos del producto.

Una linea JSON por evento, un archivo por corrida. Es la fuente de evidencia de
la columna "senal en el registro" del modelo de amenazas y de la evaluacion
adversarial.

Lo que este registro SI captura y lo que NO captura esta documentado en
docs/arquitectura.md y se contrasta fila por fila en docs/modelo-de-amenazas.md.
"""
from __future__ import annotations

import datetime as _dt
import json
import pathlib
import uuid
from typing import Any

from . import config


def _ahora() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="milliseconds")


class Registro:
    """Escribe eventos a un archivo JSONL."""

    def __init__(self, nombre_corrida: str | None = None, directorio: pathlib.Path | None = None):
        directorio = directorio or config.DIR_REGISTROS
        directorio.mkdir(parents=True, exist_ok=True)
        marca = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.nombre_corrida = nombre_corrida or f"corrida-{marca}"
        self.ruta = directorio / f"{self.nombre_corrida}.jsonl"
        self.id_corrida = str(uuid.uuid4())[:8]

    def escribir(self, tipo: str, **campos: Any) -> dict[str, Any]:
        evento = {
            "marca_tiempo": _ahora(),
            "id_corrida": self.id_corrida,
            "tipo": tipo,
            **campos,
        }
        with self.ruta.open("a", encoding="utf-8") as f:
            f.write(json.dumps(evento, ensure_ascii=False) + "\n")
        return evento

    # --- eventos del ciclo de una consulta ---

    def consulta_recibida(self, id_consulta: str, id_sesion: str, id_usuario: str, texto: str) -> None:
        self.escribir(
            "consulta_recibida",
            id_consulta=id_consulta,
            id_sesion=id_sesion,
            id_usuario=id_usuario,
            consulta=texto,
        )

    def documentos_recuperados(self, id_consulta: str, documentos: list[dict[str, Any]]) -> None:
        self.escribir(
            "documentos_recuperados",
            id_consulta=id_consulta,
            documentos=[
                {
                    "id": d["id"],
                    "titulo": d["titulo"],
                    "clasificacion": d["clasificacion"],
                    "puntaje": round(float(d["puntaje"]), 4),
                }
                for d in documentos
            ],
        )

    def memoria_recuperada(self, id_consulta: str, id_usuario: str, entradas: list[dict[str, Any]]) -> None:
        self.escribir(
            "memoria_recuperada",
            id_consulta=id_consulta,
            id_usuario=id_usuario,
            cantidad=len(entradas),
            entradas=entradas,
        )

    def herramienta_invocada(
        self, id_consulta: str, nombre: str, argumentos: dict[str, Any], resultado: Any, permitida: bool
    ) -> None:
        self.escribir(
            "herramienta_invocada",
            id_consulta=id_consulta,
            herramienta=nombre,
            argumentos=argumentos,
            permitida=permitida,
            resultado=resultado,
        )

    def control_evaluado(self, id_consulta: str, control: str, decision: str, motivo: str) -> None:
        self.escribir(
            "control_evaluado",
            id_consulta=id_consulta,
            control=control,
            decision=decision,
            motivo=motivo,
        )

    def respuesta_entregada(
        self, id_consulta: str, respuesta: str, proveedor: str, modelo: str, semilla: int
    ) -> None:
        self.escribir(
            "respuesta_entregada",
            id_consulta=id_consulta,
            respuesta=respuesta,
            proveedor=proveedor,
            modelo=modelo,
            semilla=semilla,
        )

    def memoria_escrita(self, id_consulta: str, id_usuario: str, entrada: dict[str, Any]) -> None:
        self.escribir(
            "memoria_escrita",
            id_consulta=id_consulta,
            id_usuario=id_usuario,
            entrada=entrada,
        )


def leer(ruta: pathlib.Path) -> list[dict[str, Any]]:
    """Lee un archivo de registro completo. Util para la evaluacion."""
    if not ruta.exists():
        return []
    with ruta.open(encoding="utf-8") as f:
        return [json.loads(linea) for linea in f if linea.strip()]
