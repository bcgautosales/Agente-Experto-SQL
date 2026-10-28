"""Orquestador del agente experto en SQL con memoria conversacional."""

from agente import decidir_herramienta, responder_pregunta, generar_consulta_sql
from modelo_ia import preguntar_ia
from memoria_agente import guardar_interaccion, construir_contexto, detectar_proyecto
from estado_proyecto import actualizar_estado_desde_solicitud, construir_resumen_proyecto


def construir_contexto_completo():
    """Une la ficha del proyecto con el historial reciente."""
    resumen_proyecto = construir_resumen_proyecto()
    contexto_conversacion = construir_contexto()
    return resumen_proyecto + "\n\nHISTORIAL RECIENTE\n=================\n" + contexto_conversacion


def crear_resultado(solicitud, herramienta, origen, respuesta):
    """Guarda la interacción y devuelve un resultado estándar."""
    guardar_interaccion(solicitud, respuesta)
    return {"herramienta": herramienta, "origen": origen, "respuesta": respuesta}


def responder_localmente(solicitud):
    """Intenta responder con la base de conocimientos local."""
    respuesta = responder_pregunta(solicitud)
    if respuesta.startswith("Todavía no tengo una respuesta local") or respuesta.startswith("No encontré una respuesta local"):
        return None
    return respuesta


def ejecutar_agente(solicitud):
    """Selecciona una herramienta y ejecuta la solicitud."""
    if not solicitud or not solicitud.strip():
        return {"herramienta": "ninguna", "origen": "python", "respuesta": "Debes escribir una solicitud."}

    detectar_proyecto(solicitud)
    actualizar_estado_desde_solicitud(solicitud)
    herramienta = decidir_herramienta(solicitud)

    # Primero se comprueba la base local, incluidos los conocimientos alimentados por el usuario.
    respuesta_local = responder_localmente(solicitud)
    if respuesta_local is not None:
        return crear_resultado(solicitud, "ensenar", "python", respuesta_local)

    if herramienta == "estado":
        return crear_resultado(solicitud, "estado", "python", construir_resumen_proyecto())

    if herramienta == "ensenar":
        contexto = construir_contexto_completo()
        respuesta = preguntar_ia(solicitud, contexto)
        return crear_resultado(solicitud, "ensenar", "gemini", respuesta)

    if herramienta == "generar_sql":
        respuesta = generar_consulta_sql(solicitud)
        return crear_resultado(solicitud, "generar_sql", "python", respuesta)

    if herramienta == "revisar_sql":
        contexto = construir_contexto()
        pregunta_ia = (
            "Revisa la consulta SQL o solicitud siguiente. Explica los errores y propone mejoras cuando corresponda.\n\n"
            "Contexto de la conversación:\n" + contexto + "\nSolicitud actual:\n" + solicitud
        )
        respuesta = preguntar_ia(pregunta_ia)
        return crear_resultado(solicitud, "revisar_sql", "gemini", respuesta)

    respuesta = preguntar_ia(solicitud, construir_contexto())
    return crear_resultado(solicitud, "ia", "gemini", respuesta)
