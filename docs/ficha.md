# Ficha del sistema

**Entregable 1** · Grupo Ciber2026 · Mesa de ayuda interna de TI

!!! warning "Sistema ficticio"
    El producto, la organización, los documentos y los usuarios son inventados.
    No corresponden a ningún sistema ni organización real, y no contienen datos
    personales ni información de ningún empleador.

## Para qué sirve y a quién

Asistente interno de mesa de ayuda de TI de **Corporación Vértice**, una
organización ficticia de unos 400 colaboradores. Resuelve en primer contacto las
consultas repetitivas que hoy consumen al nivel 1 de la mesa de ayuda:
restablecimiento de contraseñas, acceso remoto, cuotas de correo, permisos de
carpetas, catálogo de software y niveles de servicio.

Tres tipos de usuario:

| Usuario | Qué hace con el asistente |
| --- | --- |
| Colaborador | Pregunta sobre procedimientos y pide que se le abra un ticket |
| Agente de mesa de ayuda (N1 y N2) | Consulta procedimientos internos y ejecuta acciones de soporte |
| Administrador de plataforma | Consulta políticas restringidas y ejecuta acciones privilegiadas |

## Componentes

Tres de los cuatro del enunciado. El clasificador de machine learning clásico
queda fuera por decisión del grupo.

| Componente | Implementación | Archivo |
| --- | --- | --- |
| **Modelo de lenguaje que consulta documentos** (obligatorio) | Recuperación BM25 sobre el corpus; el modelo recibe los documentos como contexto. Proveedor configurable: API de Gemini en su nivel gratuito, o un modelo local de prueba sin red | `src/recuperacion.py`, `src/modelo.py` |
| **Agente que ejecuta acciones con herramientas** | Catálogo cerrado de tres herramientas simuladas: abrir ticket, consultar ticket, restablecer acceso | `src/herramientas.py` |
| **Memoria entre sesiones** | Historial corto por usuario, persistido en disco y recuperado al inicio de cada consulta | `src/memoria.py` |

El orquestador que une los tres y escribe el registro es `src/asistente.py`.

## Qué datos usa y de dónde vienen

| Dato | Origen | Volumen |
| --- | --- | --- |
| Corpus documental | Redactado por el grupo, íntegramente inventado | 14 documentos en `datos/corpus/` |
| Usuarios y permisos | Inventados por el grupo | 4 usuarios en `datos/usuarios.json` |
| Instrucciones internas | Definidas en `src/config.py` | Incluyen un **dato reservado sintético** |
| Memoria | Generada por el uso del propio prototipo | `datos/memoria/`, no versionada |
| Registro de eventos | Generado por cada corrida | `registros/`, se versiona solo una muestra |

Cada documento del corpus lleva una clasificación — `publico`, `interno` o
`restringido` — que define quién puede verlo.

El **dato reservado** es una clave de acceso de emergencia inventada que vive en
las instrucciones internas, no en el corpus. Es el activo que persiguen las
amenazas de confidencialidad del modelo de amenazas, equivalente a la clave
reservada de la demostración de la sesión 1.

## Quién lo usa y con qué permisos

| Id | Usuario | Rol | Documentos que puede ver | Herramientas autorizadas |
| --- | --- | --- | --- | --- |
| u-001 | Ana Quispe | colaborador | público | abrir ticket, consultar ticket |
| u-002 | Bruno Salas | soporte_n1 | público, interno | abrir ticket, consultar ticket |
| u-003 | Carla Méndez | soporte_n2 | público, interno | las tres |
| u-004 | Diego Rojas | administrador | público, interno, restringido | las tres |

`restablecer_acceso` es la única herramienta marcada como irreversible y está
reservada a `soporte_n2` y `administrador`.

## Estado en el hito 1

El producto corre y responde sobre sus documentos. Los tres interruptores de
control — mínimo privilegio en la recuperación, aislamiento de memoria y lista
blanca de herramientas — **existen en el código pero vienen desactivados por
defecto**: esa es deliberadamente la línea base sin control que la sesión 6 debe
medir. Las implementaciones de control propias del grupo irán en `controles/` a
partir de la sesión 4.
