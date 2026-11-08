"""Orquestador del producto.

Une los tres componentes: recuperacion sobre el corpus, agente con herramientas y
memoria entre sesiones. Escribe cada paso en el registro de eventos.

Los interruptores de `Controles` vienen DESACTIVADOS por defecto. Esa es la
linea base del producto, la que la sesion 6 mide "sin control". Las
implementaciones de control propias viven en controles/ y se miden en la sesion 7.
"""
from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from typing import Any

from . import config, corpus as _corpus, herramientas, modelo as _modelo
from .memoria import Memoria
from .recuperacion import IndiceBM25
from .registro import Registro


@dataclass
class Controles:
    """Interruptores de control. Desactivados = linea base sin control."""

    minimo_privilegio: bool = False
    aislamiento_memoria: bool = False
    lista_blanca_herramientas: bool = False


@dataclass
class Respuesta:
    id_consulta: str
    texto: str
    documentos: list[dict[str, Any]]
    herramientas: list[dict[str, Any]]
    memoria: list[dict[str, Any]]


_PATRON_TICKET = re.compile(r"(?i)\b(TCK-\d{4})\b")


class Asistente:
    def __init__(
        self,
        registro: Registro | None = None,
        controles: Controles | None = None,
        proveedor: str | None = None,
        memoria: Memoria | None = None,
    ):
        self.documentos = _corpus.cargar()
        self.indice = IndiceBM25(self.documentos)
        self.usuarios = json.loads(config.RUTA_USUARIOS.read_text(encoding="utf-8"))
        self.controles = controles or Controles()
        self.registro = registro or Registro()
        self.modelo = _modelo.obtener_modelo(proveedor)
        self.memoria = memoria or Memoria(aislar=self.controles.aislamiento_memoria)

    # --- agente ---

    def _planificar_herramientas(self, consulta: str) -> list[tuple[str, dict[str, Any]]]:
        """Decide que herramientas invocar. Reglas explicitas, sin modelo."""
        plan: list[tuple[str, dict[str, Any]]] = []
        baja = consulta.lower()

        encontrado = _PATRON_TICKET.search(consulta)
        if encontrado and any(p in baja for p in ("estado", "como va", "consultar", "seguimiento")):
            plan.append(("consultar_ticket", {"id_ticket": encontrado.group(1).upper()}))

        if any(p in baja for p in ("abrir un ticket", "abre un ticket", "crear ticket", "registra un ticket")):
            prioridad = "alta" if any(p in baja for p in ("urgente", "critico", "incidente")) else "media"
            plan.append(("abrir_ticket", {"titulo": consulta.strip(), "prioridad": prioridad}))

        if any(p in baja for p in ("restablecer acceso", "restablece el acceso", "resetear acceso")):
            objetivo = re.search(r"(?i)(?:de|a|para)\s+([a-z]+\.[a-z]+)", consulta)
            plan.append(
                ("restablecer_acceso", {"usuario_objetivo": objetivo.group(1) if objetivo else "desconocido"})
            )
        return plan

    # --- ciclo completo ---

    def responder(self, consulta: str, id_usuario: str = "u-001", id_sesion: str | None = None) -> Respuesta:
        id_consulta = str(uuid.uuid4())[:8]
        id_sesion = id_sesion or f"ses-{uuid.uuid4().hex[:6]}"
        usuario = self.usuarios.get(id_usuario, {})
        rol = usuario.get("rol", "colaborador")

        self.registro.consulta_recibida(id_consulta, id_sesion, id_usuario, consulta)

        # 1. Memoria entre sesiones
        self.memoria.aislar = self.controles.aislamiento_memoria
        entradas_memoria = self.memoria.recuperar(id_usuario)
        self.registro.memoria_recuperada(id_consulta, id_usuario, entradas_memoria)

        # 2. Recuperacion
        permitidas = usuario.get("clasificaciones_permitidas") if self.controles.minimo_privilegio else None
        self.registro.control_evaluado(
            id_consulta,
            "minimo_privilegio",
            "activo" if self.controles.minimo_privilegio else "inactivo",
            f"clasificaciones permitidas: {permitidas}",
        )
        documentos = self.indice.buscar(consulta, clasificaciones_permitidas=permitidas)
        self.registro.documentos_recuperados(id_consulta, documentos)

        # 3. Agente
        invocaciones: list[dict[str, Any]] = []
        for nombre, argumentos in self._planificar_herramientas(consulta):
            permitida, resultado = herramientas.invocar(
                nombre,
                argumentos,
                rol_usuario=rol,
                id_usuario=id_usuario,
                aplicar_lista_blanca=self.controles.lista_blanca_herramientas,
            )
            self.registro.herramienta_invocada(id_consulta, nombre, argumentos, resultado, permitida)
            invocaciones.append(
                {"herramienta": nombre, "argumentos": argumentos, "permitida": permitida, "resultado": resultado}
            )

        # 4. Modelo de lenguaje
        contexto = self._armar_contexto(documentos, entradas_memoria, invocaciones)
        texto = self.modelo.responder(config.INSTRUCCIONES_INTERNAS, contexto, consulta)
        self.registro.respuesta_entregada(
            id_consulta, texto, self.modelo.proveedor, self.modelo.nombre, config.SEMILLA
        )

        # 5. Memoria
        entrada = self.memoria.escribir(id_usuario, f"Consulto: {consulta.strip()}", id_consulta)
        self.registro.memoria_escrita(id_consulta, id_usuario, entrada)

        return Respuesta(id_consulta, texto, documentos, invocaciones, entradas_memoria)

    @staticmethod
    def _armar_contexto(
        documentos: list[dict[str, Any]],
        entradas_memoria: list[dict[str, Any]],
        invocaciones: list[dict[str, Any]],
    ) -> str:
        bloques: list[str] = []
        for d in documentos:
            bloques.append(f"[{d['id']} · {d['titulo']} · {d['clasificacion']}]\n{d['texto']}")
        if entradas_memoria:
            lineas = "\n".join(f"- {e['marca_tiempo']}: {e['resumen']}" for e in entradas_memoria)
            bloques.append(f"[memoria del usuario]\n{lineas}")
        for inv in invocaciones:
            bloques.append(
                f"[resultado de herramienta · {inv['herramienta']}]\n{json.dumps(inv['resultado'], ensure_ascii=False)}"
            )
        return "\n\n---\n\n".join(bloques)
