# Mesa de ayuda interna de TI

Trabajo integrador del curso **Ciberseguridad de Inteligencia Artificial** ·
Maestría en Ciencia de Datos, Universidad Nacional de Ingeniería · Grupo
**Ciber2026**.

Página publicada: **https://normanuni.github.io/grupo_2-mesa-ayuda-ti/**

> **Producto ficticio, datos sintéticos.** La organización, los documentos, los
> usuarios y las credenciales de este repositorio son inventados. No
> corresponden a ningún sistema ni organización real, y no contienen datos
> personales ni información de ningún empleador.

## Qué es

Un asistente interno de mesa de ayuda de TI con tres componentes:

1. **Modelo de lenguaje que consulta documentos** — recuperación BM25 sobre un
   corpus sintético de 14 manuales y políticas de TI.
2. **Agente que ejecuta acciones con herramientas** — catálogo cerrado de tres
   herramientas simuladas sobre un sistema de tickets.
3. **Memoria entre sesiones** — historial corto por usuario.

Cada consulta, los documentos recuperados, las herramientas invocadas y la
respuesta quedan en un registro de eventos en `registros/`.

El objetivo del trabajo no es el asistente, sino atacarlo, defenderlo y **medir**
el resultado.

## Instalación

Requiere Python 3.10 o superior.

```bash
git clone https://github.com/NormanUNI/grupo_2-mesa-ayuda-ti.git
cd grupo_2-mesa-ayuda-ti
```

El prototipo **corre sin instalar nada** en su modo de prueba local, que no usa
red ni llave de API:

```bash
python -m src.cli --consulta "Cual es el plazo para reportar un incidente?"
```

Para usar la API de Gemini en su nivel gratuito:

```bash
pip install -r requirements.txt
cp .env.example .env     # colocar la llave en GEMINI_API_KEY
export PROVEEDOR_MODELO=gemini
python -m src.cli
```

La llave vive en `.env`, excluido por `.gitignore`, y nunca entra al historial
del repositorio.

## Cómo correrlo

```bash
# sesión interactiva como colaborador
python -m src.cli

# una consulta, como administrador, con los tres controles activados
python -m src.cli --usuario u-004 --controles --consulta "Politica de cuentas privilegiadas"

# el agente ejecuta herramientas
python -m src.cli --usuario u-003 --consulta "Abrir un ticket urgente por la VPN"
```

Opciones:

| Opción | Qué hace |
| --- | --- |
| `--consulta` | Una sola consulta en lugar del modo interactivo |
| `--usuario` | Usuario sintético, de `u-001` a `u-004`. Por defecto `u-001` |
| `--proveedor` | `eco` (local, sin red) o `gemini` |
| `--controles` | Activa mínimo privilegio, aislamiento de memoria y lista blanca |
| `--corrida` | Nombre del archivo de registro |

### Los controles vienen desactivados

Por defecto los tres interruptores de control están **apagados**. Esa es
deliberadamente la línea base sin control que la sesión 6 debe medir. Correr con
`--controles` muestra la diferencia:

```bash
# un colaborador recupera un documento restringido
python -m src.cli --usuario u-001 --consulta "cuentas privilegiadas de emergencia"

# con control, no lo recupera
python -m src.cli --usuario u-001 --controles --consulta "cuentas privilegiadas de emergencia"
```

## Estructura

```
docs/                      documentación y fuente de la página
  index.md                 portada
  ficha.md                 entregable 1
  arquitectura.md          entregable 2, con el diagrama en Mermaid
  modelo-de-amenazas.md    entregable 3
  priorizacion.md          entregable 4
  controles.md             entregable 5
  evaluacion.md            entregable 6
  regulatorio.md           entregable 7
src/                       el producto
  config.py                instrucciones internas y dato reservado sintético
  registro.py              registro de eventos en JSONL
  corpus.py                carga del corpus
  recuperacion.py          índice BM25
  modelo.py                proveedores de modelo: gemini y eco
  herramientas.py          catálogo del agente
  memoria.py               memoria entre sesiones
  asistente.py             orquestador
  cli.py                   línea de comandos
controles/                 controles implementados por el grupo (sesión 4 en adelante)
datos/
  corpus/                  14 documentos sintéticos
  usuarios.json            usuarios sintéticos y permisos
evaluacion/
  catalogo/                ataques y consultas legítimas
  resultados/              JSON y gráficos de cada corrida
registros/                 muestra del registro de una corrida
requirements.txt
.env.example               nombres de las variables, sin valores
```

## La página

Se construye desde `docs/` con MkDocs y el tema Material, que dibuja los
diagramas Mermaid. El despliegue a GitHub Pages es automático en cada push a
`main`, con el flujo de `.github/workflows/pages.yml`.

Para verla antes de publicar:

```bash
pip install -r requirements.txt
mkdocs serve
```

Para que el despliegue funcione, en GitHub: **Settings → Pages → Source → GitHub
Actions**.

## Reglas del trabajo

- **Datos.** Solo datos sintéticos, en el código, en los registros, en la página
  y en la presentación.
- **Credenciales.** Ninguna llave en el repositorio ni en su historial.
- **Ataques.** Solo contra el producto de este repositorio. Nunca contra
  servicios de terceros ni sistemas reales.
- **Entrega final.** El estado del repositorio en la etiqueta de git
  `entrega-final`, publicada antes del inicio de la sesión 8.
