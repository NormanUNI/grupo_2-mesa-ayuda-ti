"""Recuperacion de documentos sobre el corpus.

Implementa BM25 sin dependencias externas: es determinista, corre en Colab sin
instalar nada y basta para el proposito del trabajo, que es estudiar la seguridad
del flujo de recuperacion y no la calidad del buscador.

Si el grupo decide pasar a embeddings, solo cambia esta clase: el resto del
producto habla con ella a traves de `buscar`.
"""
from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from typing import Any

from . import config

_PALABRAS_VACIAS = {
    "a", "al", "ante", "con", "como", "cuando", "de", "del", "desde", "donde",
    "el", "en", "entre", "es", "esta", "este", "hasta", "la", "las", "lo", "los",
    "mas", "me", "mi", "no", "o", "para", "pero", "por", "que", "se", "si", "sin",
    "sobre", "su", "sus", "te", "tu", "un", "una", "uno", "y", "ya",
}


def normalizar(texto: str) -> list[str]:
    """Minusculas, sin tildes, solo palabras, sin palabras vacias."""
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    fichas = re.findall(r"[a-z0-9]+", texto)
    return [f for f in fichas if f not in _PALABRAS_VACIAS and len(f) > 2]


class IndiceBM25:
    """Indice BM25 sobre los documentos del corpus."""

    def __init__(self, documentos: list[dict[str, Any]], k1: float = 1.5, b: float = 0.75):
        self.documentos = documentos
        self.k1 = k1
        self.b = b
        self._fichas = [Counter(normalizar(d["texto"] + " " + d["titulo"])) for d in documentos]
        self._largos = [sum(c.values()) for c in self._fichas]
        self._largo_medio = (sum(self._largos) / len(self._largos)) if self._largos else 0.0
        self._frecuencia_documental: Counter[str] = Counter()
        for conteo in self._fichas:
            self._frecuencia_documental.update(conteo.keys())
        self._n = len(documentos)

    def _idf(self, ficha: str) -> float:
        n_q = self._frecuencia_documental.get(ficha, 0)
        return math.log((self._n - n_q + 0.5) / (n_q + 0.5) + 1.0)

    def puntuar(self, consulta: str) -> list[tuple[int, float]]:
        fichas_consulta = normalizar(consulta)
        puntajes: list[tuple[int, float]] = []
        for i, conteo in enumerate(self._fichas):
            total = 0.0
            largo = self._largos[i] or 1
            for ficha in fichas_consulta:
                f = conteo.get(ficha, 0)
                if not f:
                    continue
                denominador = f + self.k1 * (1 - self.b + self.b * largo / (self._largo_medio or 1))
                total += self._idf(ficha) * f * (self.k1 + 1) / denominador
            puntajes.append((i, total))
        # Orden estable: por puntaje descendente y, a igual puntaje, por indice.
        puntajes.sort(key=lambda par: (-par[1], par[0]))
        return puntajes

    def buscar(
        self,
        consulta: str,
        k: int | None = None,
        clasificaciones_permitidas: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Devuelve los k documentos mas relevantes.

        `clasificaciones_permitidas` aplica el filtro de minimo privilegio. Si se
        pasa None, el indice devuelve todo el corpus: ese es el comportamiento
        SIN control, el que la evaluacion adversarial mide como linea base.
        """
        k = k or config.DOCUMENTOS_POR_CONSULTA
        resultados: list[dict[str, Any]] = []
        for i, puntaje in self.puntuar(consulta):
            if puntaje <= 0:
                continue
            documento = self.documentos[i]
            if (
                clasificaciones_permitidas is not None
                and documento["clasificacion"] not in clasificaciones_permitidas
            ):
                continue
            resultados.append({**documento, "puntaje": puntaje})
            if len(resultados) >= k:
                break
        return resultados
