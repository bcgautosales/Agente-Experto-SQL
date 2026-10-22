
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
)


def crear_resultado(solicitud, herramienta, origen, respuesta):
    """Guarda la interacción y devuelve un resultado estándar."""

    guardar_interaccion(solicitud, respuesta)

    return {
        "herramienta": herramienta,
        "origen": origen,
        "respuesta": respuesta,
    }


def ejecutar_agente(solicitud):
    """Selecciona una herramienta y ejecuta la solicitud."""

    if not solicitud or solicitud.strip() == "":
        return {
            "herramienta": "ninguna",
            "origen": "python",
            "respuesta": "Debes escribir una solicitud.",
        }

    herramienta = decidir_herramienta(solicitud)

    if herramienta == "ensenar":
        componente = detectar_componente(solicitud)

        if componente:
            respuesta = responder_pregunta(solicitud)

            return crear_resultado(
                solicitud,
                "ensenar",
                "python",
                respuesta,
            )

        contexto = construir_contexto()
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
