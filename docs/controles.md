# Controles y riesgo residual

**Entregable 5** · Grupo Ciber2026

> En construcción. Los controles se diseñan en la sesión 4 y se implementan y
> miden entre las sesiones 4 y 7.

Para cada una de las cinco amenazas prioritarias: qué control se propone, **qué
detecta** y **qué deja pasar**. Lo que queda sin cubrir es el riesgo residual.

Al menos dos controles deben estar implementados en el código, en `controles/`.

## Interruptores ya presentes en el producto

Los tres interruptores existen en `src/asistente.py` (clase `Controles`) y vienen
desactivados por defecto, que es la línea base sin control que mide la sesión 6.

| Interruptor | Qué hace cuando se activa | Dónde actúa |
| --- | --- | --- |
| `minimo_privilegio` | Filtra el corpus por las clasificaciones que el rol del usuario puede ver | `recuperacion.IndiceBM25.buscar` |
| `aislamiento_memoria` | Recupera solo la memoria del usuario que consulta | `memoria.Memoria.recuperar` |
| `lista_blanca_herramientas` | Verifica el rol y los argumentos antes de ejecutar una herramienta | `herramientas.invocar` |

| Control | Qué detecta | Qué deja pasar |
| --- | --- | --- |
| _pendiente sesión 4_ | | |
