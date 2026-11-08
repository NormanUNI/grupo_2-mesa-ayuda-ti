---
id: doc-013
titulo: Continuidad y respaldos
area: Plataforma
clasificacion: restringido
origen: sintetico
---

# Continuidad y respaldos

Los sistemas se clasifican en criticos, importantes y de soporte segun el impacto
de su indisponibilidad.

Objetivos por clasificacion:

- Criticos: recuperacion en cuatro horas, perdida maxima de datos de quince
  minutos.
- Importantes: recuperacion en veinticuatro horas, perdida maxima de cuatro horas.
- De soporte: recuperacion en setenta y dos horas, perdida maxima de un dia.

Los respaldos se ejecutan diariamente y se conservan treinta dias en linea y doce
meses en almacenamiento frio. Una copia se mantiene en una sede distinta.

Las pruebas de restauracion se realizan trimestralmente sobre una muestra de
sistemas y sus resultados se documentan. Un respaldo que no se ha restaurado nunca
no se considera un respaldo valido.

La invocacion del plan de continuidad corresponde al comite de crisis. La mesa de
ayuda no declara contingencias.
