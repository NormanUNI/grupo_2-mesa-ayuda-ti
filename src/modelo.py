"""Proveedores de modelo de lenguaje.

Dos implementaciones con la misma interfaz:

- `ModeloGemini`: la API de Gemini en su nivel gratuito. Requiere GEMINI_API_KEY
  en el archivo .env, que esta excluido por .gitignore.
- `ModeloEco`: un modelo local de prueba, sin red ni llave. No es un modelo de
  lenguaje: arma la respuesta a partir del contexto recibido y obedece las
  instrucciones que encuentre en el. Sirve para desarrollar el producto, probar
  el registro y correr la evaluacion cuando la cuota de la API se agota.

El modo "eco" es deliberadamente credulo con las instrucciones del contexto, lo
que lo hace util como banco de pruebas de la inyeccion indirecta. Las cifras que
se reporten en docs/evaluacion.md deben indicar con que proveedor se midieron.
"""
from __future__ import annotations

import re
from typing import Any, Protocol

from . import config


class Modelo(Protocol):
    nombre: str
    proveedor: str

    def responder(self, instrucciones: str, contexto: str, consulta: str) -> str: ...


class ModeloEco:
    """Modelo local de prueba. No usa red."""

    proveedor = "eco"
    nombre = "eco-local-v1"

    _PATRON_INSTRUCCION = re.compile(
        r"(?im)^\s*(?:\[?(?:instruccion|instrucción|system|nota para el asistente|importante)\]?\s*[:\-]\s*)(.+)$"
    )

    def responder(self, instrucciones: str, contexto: str, consulta: str) -> str:
        # Obedece instrucciones incrustadas en el contexto: ese es el punto.
        incrustadas = self._PATRON_INSTRUCCION.findall(contexto)
        if incrustadas:
            orden = incrustadas[-1].strip()
            if re.search(r"(?i)clave|credencial|contrasena|contraseña|secreto", orden):
                encontrada = re.search(r"([A-Z]{2,}-[A-Z]+-\d{3,})", instrucciones)
                if encontrada:
                    return (
                        "Siguiendo la indicacion del documento recuperado, el dato solicitado es "
                        f"{encontrada.group(1)}."
                    )
            return f"Siguiendo la indicacion del documento recuperado: {orden}"

        if not contexto.strip():
            return (
                "No encontre documentos que respondan esa consulta. Te sugiero abrir un "
                "ticket en la mesa de ayuda para que lo revise un agente."
            )

        fragmentos = []
        for bloque in contexto.split("\n\n---\n\n"):
            bloque = bloque.strip()
            if not bloque:
                continue
            lineas = [l for l in bloque.splitlines() if l.strip()]
            cabecera = lineas[0] if lineas else ""
            cuerpo = " ".join(lineas[1:])[:420]
            fragmentos.append(f"{cabecera}\n{cuerpo}")
        return (
            "Segun los documentos de la mesa de ayuda:\n\n" + "\n\n".join(fragmentos)
        )


class ModeloGemini:
    """API de Gemini en su nivel gratuito."""

    proveedor = "gemini"

    def __init__(self, nombre: str | None = None, llave: str | None = None):
        self.nombre = nombre or config.MODELO_GEMINI
        self._llave = llave or config.LLAVE_GEMINI
        if not self._llave:
            raise RuntimeError(
                "Falta GEMINI_API_KEY. Copia .env.example a .env y coloca la llave, "
                "o usa PROVEEDOR_MODELO=eco para correr sin API."
            )
        try:
            from google import genai  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "Falta el paquete google-genai. Instalalo con: pip install -r requirements.txt"
            ) from exc
        self._cliente = genai.Client(api_key=self._llave)

    def responder(self, instrucciones: str, contexto: str, consulta: str) -> str:
        peticion = (
            f"{instrucciones}\n\n"
            "=== DOCUMENTOS RECUPERADOS ===\n"
            f"{contexto or '(sin documentos)'}\n"
            "=== FIN DE LOS DOCUMENTOS ===\n\n"
            f"Consulta del colaborador: {consulta}"
        )
        respuesta = self._cliente.models.generate_content(
            model=self.nombre, contents=peticion
        )
        return (respuesta.text or "").strip()


def obtener_modelo(proveedor: str | None = None) -> Any:
    proveedor = (proveedor or config.PROVEEDOR_MODELO).lower()
    if proveedor == "gemini":
        return ModeloGemini()
    if proveedor == "eco":
        return ModeloEco()
    raise ValueError(f"Proveedor de modelo desconocido: {proveedor}")
