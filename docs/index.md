# Mesa de ayuda interna de TI

Trabajo integrador del curso **Ciberseguridad de Inteligencia Artificial** ·
Maestría en Ciencia de Datos, Universidad Nacional de Ingeniería.

Grupo **Ciber2026**.

!!! warning "Producto ficticio, datos sintéticos"
    Todo lo que se ve en esta página — la organización, los documentos, los
    usuarios y las credenciales — es inventado. No corresponde a ningún sistema
    ni organización real.

## Qué es

Un asistente interno de mesa de ayuda de TI que responde sobre manuales y
políticas usando recuperación sobre un corpus documental sintético, ejecuta
acciones de soporte a través de herramientas, y mantiene memoria entre sesiones.

El objetivo del trabajo no es el asistente: es **atacarlo, defenderlo y medir**
qué tan efectiva resulta esa defensa.

## Dónde va cada cosa

| Documento | Qué contiene | Estado |
| --- | --- | --- |
| [Ficha del sistema](ficha.md) | Para qué sirve, componentes, datos y permisos | Hito 1 |
| [Arquitectura](arquitectura.md) | Diagrama, límites de confianza y qué registra el producto | Hito 1 |
| [Modelo de amenazas](modelo-de-amenazas.md) | Una fila por amenaza, con sus nueve columnas | En avance, sesiones 3 a 6 |
| [Priorización](priorizacion.md) | Amenazas ordenadas por explotabilidad e impacto | Sesión 3 en adelante |
| [Controles y riesgo residual](controles.md) | Qué detecta y qué deja pasar cada control | Sesión 4 en adelante |
| [Evaluación adversarial](evaluacion.md) | Tasas medidas con su intervalo de Wilson | Sesiones 6 y 7 |
| [Clasificación regulatoria](regulatorio.md) | Normativa peruana y reglamento europeo | Sesión 7 |

## Estado del trabajo

| Sesión | Qué debe existir | Estado |
| --- | --- | --- |
| 3 | Grupo registrado, producto elegido, repositorio creado | Hecho |
| 4 | **Hito 1:** ficha, arquitectura, estructura del repositorio, página publicada, asistente respondiendo | Hecho |
| 6 | **Hito 2:** tres componentes, registro, modelo en avance, primera medición sin control | Pendiente |
| 7 | Controles implementados y medidos, clasificación regulatoria | Pendiente |
| 8 | Etiqueta `entrega-final` y sustentación | Pendiente |

## Probarlo

El asistente **no corre en esta página**. GitHub Pages entrega archivos estáticos y no
ejecuta Python, y el enunciado del trabajo restringe el alcance a un prototipo local o
en Colab, sin desplegarlo en internet. Esta página es la documentación del producto, no
el producto.

Hay dos formas de usarlo.

### En el navegador, con Colab

Sin instalar nada y sin llave de API:

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NormanUNI/grupo_2-mesa-ayuda-ti/blob/main/notebooks/mesa_de_ayuda.ipynb)

El notebook clona el repositorio, carga el asistente y trae consultas de ejemplo,
incluidas las dos amenazas que ya se pueden demostrar con el producto en su estado
actual: recuperación sin mínimo privilegio y abuso de herramientas del agente.

### En tu máquina

```bash
git clone https://github.com/NormanUNI/grupo_2-mesa-ayuda-ti.git
cd grupo_2-mesa-ayuda-ti
python -m src.cli --consulta "Cual es el plazo para reportar un incidente?"
```

Requiere Python 3.10 o superior. Corre sin instalar nada y sin llave de API en su modo
de prueba local. Las instrucciones completas están en el README del repositorio.
