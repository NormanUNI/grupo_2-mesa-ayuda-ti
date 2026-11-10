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

    def __init__(
        self,
        nombre: str | None = None,
        llave: str | None = None,
        tiempo_limite: float = 60.0,
    ):
        self.nombre = nombre or config.MODELO_GEMINI
        self._llave = llave or config.LLAVE_GEMINI
        self._tiempo_limite = tiempo_limite
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
        self._usa_interactions = hasattr(self._cliente, "interactions")

    @staticmethod
    def _extraer_texto(respuesta: Any) -> str:
        """Saca el texto de la respuesta sin asumir una sola forma.

        La Interactions API devuelve `output_text`; generate_content devuelve
        `text`. Si Google cambia la envoltura, el recorrido final evita que el
        prototipo se caiga sin decir nada util.
        """
        for atributo in ("output_text", "text"):
            valor = getattr(respuesta, atributo, None)
            if isinstance(valor, str) and valor.strip():
                return valor.strip()
        salida = getattr(respuesta, "output", None)
        if salida:
            partes: list[str] = []
            for elemento in salida if isinstance(salida, list) else [salida]:
                contenido = getattr(elemento, "content", None) or []
                for parte in contenido if isinstance(contenido, list) else [contenido]:
                    texto = getattr(parte, "text", None)
                    if isinstance(texto, str):
                        partes.append(texto)
            if partes:
                return "\n".join(partes).strip()
        raise RuntimeError(
            "La respuesta del modelo no trae texto reconocible. "
            f"Campos disponibles: {sorted(d for d in dir(respuesta) if not d.startswith('_'))[:15]}"
        )

    def responder(self, instrucciones: str, contexto: str, consulta: str) -> str:
        peticion = (
            f"{instrucciones}\n\n"
            "=== DOCUMENTOS RECUPERADOS ===\n"
            f"{contexto or '(sin documentos)'}\n"
            "=== FIN DE LOS DOCUMENTOS ===\n\n"
            f"Consulta del colaborador: {consulta}"
        )
        if self._usa_interactions:
            # Interactions API: interfaz vigente desde junio de 2026. Los modelos
            # de la serie 3.x no responden por el endpoint generate_content, que
            # se queda esperando sin devolver error.
            respuesta = self._cliente.interactions.create(
                model=self.nombre,
                input=peticion,
                timeout=self._tiempo_limite,
            )
        else:  # SDK anterior a la Interactions API
            respuesta = self._cliente.models.generate_content(
                model=self.nombre, contents=peticion
            )
        return self._extraer_texto(respuesta)


class ModeloDeepSeek:
    """API de DeepSeek, en su formato compatible con OpenAI.

    A diferencia de la ruta de Gemini, aqui las instrucciones internas viajan
    como mensaje `system` y los documentos recuperados como mensaje `user`. Esa
    separacion importa para el modelo de amenazas: es la frontera que una
    inyeccion indirecta intenta cruzar, y medirla con los dos canales separados
    da un resultado mas fiel que concatenarlo todo en un solo texto.
    """

    proveedor = "deepseek"

    def __init__(
        self,
        nombre: str | None = None,
        llave: str | None = None,
        url: str | None = None,
        tiempo_limite: float = 60.0,
    ):
        self.nombre = nombre or config.MODELO_DEEPSEEK
        self._llave = llave or config.LLAVE_DEEPSEEK
        self._url = url or config.URL_DEEPSEEK
        if not self._llave:
            raise RuntimeError(
                "Falta DEEPSEEK_API_KEY. Copia .env.example a .env y coloca la llave, "
                "o usa PROVEEDOR_MODELO=eco para correr sin API."
            )
        try:
            from openai import OpenAI  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "Falta el paquete openai, que DeepSeek usa por compatibilidad. "
                "Instalalo con: pip install -r requirements.txt"
            ) from exc
        self._cliente = OpenAI(
            api_key=self._llave, base_url=self._url, timeout=tiempo_limite
        )

    def responder(self, instrucciones: str, contexto: str, consulta: str) -> str:
        mensaje_usuario = (
            "=== DOCUMENTOS RECUPERADOS ===\n"
            f"{contexto or '(sin documentos)'}\n"
            "=== FIN DE LOS DOCUMENTOS ===\n\n"
            f"Consulta del colaborador: {consulta}"
        )
        respuesta = self._cliente.chat.completions.create(
            model=self.nombre,
            messages=[
                {"role": "system", "content": instrucciones},
                {"role": "user", "content": mensaje_usuario},
            ],
            stream=False,
        )
        return (respuesta.choices[0].message.content or "").strip()


def obtener_modelo(proveedor: str | None = None) -> Any:
    proveedor = (proveedor or config.PROVEEDOR_MODELO).lower()
    if proveedor == "deepseek":
        return ModeloDeepSeek()
    if proveedor == "gemini":
        return ModeloGemini()
    if proveedor == "eco":
        return ModeloEco()
    raise ValueError(f"Proveedor de modelo desconocido: {proveedor}")
