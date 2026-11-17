# Ejemplos de prueba del arnés

**No son el catálogo de medición.** Son tres casos por archivo para comprobar que
`correr_evaluacion.py` lee el registro y decide bien el éxito. Las cifras que se
publican salen de `evaluacion/catalogo/`, que se fija en git antes de la primera
corrida.

Cada archivo incluye un control negativo (el tercer caso) que no debería contar
como éxito ni sin control.

```bash
python evaluacion/correr_evaluacion.py --catalogo evaluacion/ejemplos/a03_ejemplo.jsonl --sin-control --salida /tmp/res
python evaluacion/correr_evaluacion.py --catalogo evaluacion/ejemplos/a03_ejemplo.jsonl --con-control --salida /tmp/res
```

Resultado esperado con el corpus de 18 documentos y el proveedor `eco`:

| Archivo | Sin control | Con control |
| --- | --- | --- |
| `a03_ejemplo.jsonl` | 2/3 | 0/3 |
| `a04_ejemplo.jsonl` | 2/3 | 0/3 |
| `a05_ejemplo.jsonl` | 2/3 | 0/3 |
| `legitimas_ejemplo.jsonl` | 0/3 bloqueadas | 0/3 bloqueadas |

Se usa `--salida /tmp/res` para que las pruebas no ensucien
`evaluacion/resultados/`, donde solo van las mediciones reales: cada medición
deja ahí su JSON y, en `evaluacion/resultados/registros/`, el registro JSONL que
la respalda. Ambos se versionan en git.
