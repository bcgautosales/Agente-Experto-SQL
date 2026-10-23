
"""
Orquestador del agente experto en SQL con memoria conversacional.
"""

from agente import (
    decidir_herramienta,
    detectar_componente,
    responder_pregunta,
    generar_consulta_sql,
)

from modelo_ia import preguntar_ia

from memoria_agente import (
    guardar_interaccion,
    construir_contexto,
    detectar_proyecto,
)
from estado_proyecto import (
    actualizar_estado_desde_solicitud,
    construir_resumen_proyecto,
)


def construir_contexto_completo():
    """Une la ficha del proyecto con el historial reciente."""

    resumen_proyecto = construir_resumen_proyecto()
    contexto_conversacion = construir_contexto()

    contexto_completo = (
        resumen_proyecto
        + "\n\nHISTORIAL RECIENTE\n"
        + "=================\n"
        + contexto_conversacion
    )

    return contexto_completo


def crear_resultado(solicitud, herramienta, origen, respuesta):
    """Guarda la interacción y devuelve un resultado estándar."""

    guardar_interaccion(solicitud, respuesta)

    return {
        "herramienta": herramienta,
        "origen": origen,
        "respuesta": respuesta,
    }


def responder_localmente(solicitud):
    """Intenta responder con la base de conocimientos local."""

    respuesta = responder_pregunta(solicitud)

    # Si el agente no conoce la respuesta, devuelve None.
    if respuesta.startswith("Todavía no tengo una respuesta local"):
        return None

    if respuesta.startswith("No encontré una respuesta local"):
        return None

    return respuesta


def ejecutar_agente(solicitud):
    """Selecciona una herramienta y ejecuta la solicitud."""

    if not solicitud or solicitud.strip() == "":
        return {
            "herramienta": "ninguna",
            "origen": "python",
            "respuesta": "Debes escribir una solicitud.",
        }
    detectar_proyecto(solicitud)

    actualizar_estado_desde_solicitud(solicitud)

    herramienta = decidir_herramienta(solicitud)

    # Intentar responder localmente antes de usar Gemini.
    respuesta_local = responder_localmente(solicitud)

    if respuesta_local is not None:
        return crear_resultado(
            solicitud,
            "ensenar",
            "python",
            respuesta_local,
        )

    if herramienta == "estado":
        respuesta = construir_resumen_proyecto()

        return crear_resultado(
            solicitud,
            "estado",
            "python",
            respuesta,
        )

    if herramienta == "ensenar":
        # Primero intentamos responder usando conocimientos locales.
        respuesta = responder_localmente(solicitud)

        if respuesta is not None:
            return crear_resultado(
                solicitud,
                "ensenar",
                "python",
                respuesta,
            )

        # Si no hay una respuesta local, recurrimos a Gemini.
        contexto = construir_contexto_completo()
        respuesta = preguntar_ia(solicitud, contexto)

        return crear_resultado(
            solicitud,
            "ensenar",
            "gemini",
            respuesta,
        )

    elif herramienta == "generar_sql":
        respuesta = generar_consulta_sql(solicitud)

        return crear_resultado(
            solicitud,
            "generar_sql",
            "python",
            respuesta,
        )

    elif herramienta == "revisar_sql":
        contexto = construir_contexto()

        pregunta = (
            "Revisa la consulta SQL o solicitud siguiente. "
            "Explica los errores y propone mejoras cuando "
            "corresponda.\n\n"
            "Contexto de la conversación:\n"
            + contexto
            + "\nSolicitud actual:\n"
            + solicitud
        )

        respuesta = preguntar_ia(pregunta)

        return crear_resultado(
            solicitud,
            "revisar_sql",
            "gemini",
            respuesta,
        )

    else:
        contexto = construir_contexto()
        respuesta = preguntar_ia(solicitud, contexto)

        return crear_resultado(
            solicitud,
            "ia",
            "gemini",
            respuesta,
        )
