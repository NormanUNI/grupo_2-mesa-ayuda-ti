---
id: doc-018
titulo: Custodia de llaves de API y secretos de integracion
area: Plataforma
clasificacion: restringido
origen: sintetico
---

# Custodia de llaves de API y secretos de integracion

Las integraciones entre sistemas usan llaves de API, certificados y cuentas de
servicio. Estos secretos dan acceso directo a los datos de la organizacion y se
tratan con el mismo cuidado que una cuenta privilegiada.

Donde viven los secretos:

- Todos los secretos se guardan en la boveda de secretos de la plataforma. No se
  escriben en el codigo, en archivos de configuracion versionados, en hojas de
  calculo ni en el sistema de tickets.
- Cada secreto tiene un responsable nominal y una fecha de vencimiento.
- Las aplicaciones leen el secreto desde la boveda al iniciar. Ninguna persona
  necesita verlo para que la integracion funcione.

Rotacion:

- Las llaves de API se rotan cada noventa dias y los certificados antes de su
  vencimiento.
- Al cesar o cambiar de area el responsable, todos sus secretos se rotan dentro de
  las cuarenta y ocho horas.

Exposicion de un secreto:

- Si un secreto aparece en un repositorio, un correo, un chat o una captura de
  pantalla, se considera comprometido aunque se borre despues.
- El procedimiento es revocarlo, emitir uno nuevo, revisar los registros de uso
  desde la fecha de exposicion y documentarlo como incidente de seguridad.
- El aviso se dirige al oficial de seguridad dentro de la primera hora.

La mesa de ayuda no entrega, consulta ni restablece secretos de integracion. Toda
solicitud relacionada se deriva al equipo de plataforma con ticket.
