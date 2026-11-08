# Evaluación adversarial

**Entregable 6** · Grupo Ciber2026

> En construcción. La primera medición sin control corresponde al hito 2
> (sesión 6); la medición con control, a la sesión 7.

## Diseño

- Al menos **tres** de las cinco amenazas prioritarias.
- Al menos **20 intentos por amenaza** y **20 consultas legítimas**.
- Cada amenaza se mide **sin control y con control**.
- Se reporta la **tasa de éxito del ataque con su intervalo de Wilson al 95%** y
  la **tasa de falsos positivos de cada control** sobre las consultas legítimas.

Un falso positivo es una consulta legítima que el control bloquea.

## Por qué Wilson y no el intervalo normal

Con 20 intentos, el intervalo clásico de Wald colapsa a cero cuando el control
bloquea todos los ataques: afirmaría con certeza que la tasa real es exactamente
cero, lo cual es falso. Wilson mantiene un ancho positivo.

El intervalo es centro ± semiancho, con z = 1,96 al 95%:

$$
\text{centro} = \frac{\hat{p} + \dfrac{z^2}{2n}}{1 + \dfrac{z^2}{n}}
\qquad
\text{semiancho} = \frac{z}{1 + \dfrac{z^2}{n}}\sqrt{\dfrac{\hat{p}(1-\hat{p})}{n} + \dfrac{z^2}{4n^2}}
$$

Donde $\hat{p} = x/n$ es la proporción observada, $n$ el número de intentos y $z$
el cuantil de la normal estándar.

Con n = 20, bloquear los 20 ataques da un intervalo de [0,000 · 0,161]: la tasa
real podría llegar al 16%. Ningún control se reporta como efectivo al 100%.

## Resultados

| Amenaza | Condición | Éxitos / intentos | Tasa | Wilson 95% |
| --- | --- | --- | --- | --- |
| _pendiente sesión 6_ | | | | |
