# Priorización

**Entregable 4** · Grupo Ciber2026

> En construcción. Se completa cuando el modelo de amenazas tenga sus filas.

Las amenazas ordenadas por **explotabilidad** (qué tan fácil es llevarlas a cabo)
e **impacto**, con la justificación escrita de las cinco primeras.

La escala se publica antes de aplicarla, para que el orden sea verificable y no
una intuición.

## Escala

| Nivel | Explotabilidad | Impacto |
| --- | --- | --- |
| 5 | Funciona con una sola consulta, sin conocimiento previo del sistema | Acción irreversible sobre un sistema externo, o fuga completa del corpus |
| 4 | Requiere agregar un documento o encadenar varias consultas | Fuga del dato reservado |
| 3 | Requiere conocer la estructura del prompt o del corpus | Respuestas incorrectas en casos concretos |
| 2 | Requiere acceso a la máquina o al repositorio | Degradación del servicio |
| 1 | Requiere privilegios que el adversario no tiene en el modelo | Molestia sin pérdida |

La prioridad es el producto de ambas. En la terminología de la sesión 1, la
explotabilidad es la versión observable de la probabilidad dentro de
`riesgo = probabilidad × impacto`.
