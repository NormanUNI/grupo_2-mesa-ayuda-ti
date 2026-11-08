"""Arnes de evaluacion adversarial.

Esqueleto del hito 1. El catalogo de ataques y consultas legitimas se construye a
partir de la sesion 3, y la primera medicion sin control corresponde al hito 2.

Lo que ya esta listo y probado: el calculo del intervalo de Wilson, que es lo que
el enunciado exige reportar junto a cada tasa.

Uso previsto:
    python evaluacion/correr_evaluacion.py --amenaza inyeccion_indirecta --sin-control
"""
from __future__ import annotations

import math


def wilson(exitos: int, intentos: int, z: float = 1.96) -> tuple[float, float, float]:
    """Intervalo de Wilson para una proporcion binomial.

    Devuelve (proporcion_observada, limite_inferior, limite_superior).

    Se usa en lugar del intervalo normal (Wald) porque con n pequeno y
    proporciones cerca de 0 o 1 el intervalo de Wald colapsa a ancho cero: con
    0 exitos de 20 afirmaria que la tasa real es exactamente 0, lo cual es falso.

        centro    = (p + z^2/2n) / (1 + z^2/n)
        semiancho = z/(1 + z^2/n) * sqrt( p(1-p)/n + z^2/4n^2 )

    donde p es la proporcion observada, n el numero de intentos y z el cuantil
    de la normal estandar (1.96 al 95%).
    """
    if intentos <= 0:
        raise ValueError("intentos debe ser mayor que cero")
    p = exitos / intentos
    z2 = z * z
    denominador = 1 + z2 / intentos
    centro = (p + z2 / (2 * intentos)) / denominador
    semiancho = (z / denominador) * math.sqrt(
        p * (1 - p) / intentos + z2 / (4 * intentos * intentos)
    )
    return p, max(0.0, centro - semiancho), min(1.0, centro + semiancho)


def tasa_falsos_positivos(bloqueadas: int, legitimas: int, z: float = 1.96) -> tuple[float, float, float]:
    """Tasa de falsos positivos de un control sobre las consultas legitimas.

    Un falso positivo es una consulta legitima que el control bloquea. Se calcula
    con el mismo intervalo, sobre el subconjunto de consultas legitimas: es un
    denominador distinto al de la tasa de exito del ataque y no se mezclan.
    """
    return wilson(bloqueadas, legitimas, z)


if __name__ == "__main__":
    # Verificacion de la formula contra los tres casos de referencia del grupo.
    for exitos, intentos in ((0, 20), (3, 20), (15, 20)):
        p, bajo, alto = wilson(exitos, intentos)
        print(f"{exitos:>3}/{intentos}  p={p:.3f}  Wilson 95% = [{bajo:.3f} , {alto:.3f}]")
    print("\nPendiente: catalogo de ataques y consultas legitimas (sesion 3 en adelante).")
