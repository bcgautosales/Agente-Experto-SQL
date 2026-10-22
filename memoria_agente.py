"""
Memoria persistente del agente experto en SQL.
Guarda el historial en un archivo JSON.
"""

import json
import os
import copy


RUTA_MEMORIA = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "memoria.json"
)

MEMORIA_INICIAL = {
    "proyecto_actual": None,
    "historial": []
}


def cargar_memoria():
    """Carga la memoria guardada o crea una memoria inicial."""

    if os.path.exists(RUTA_MEMORIA):
        try:
            with open(
                RUTA_MEMORIA,
                "r",
                encoding="utf-8"
            ) as archivo:
                datos = json.load(archivo)

            if (
                isinstance(datos, dict)
                and isinstance(datos.get("historial"), list)
                and "proyecto_actual" in datos
            ):
                return datos

        except (json.JSONDecodeError, OSError):
            pass

    return copy.deepcopy(MEMORIA_INICIAL)


memoria = cargar_memoria()


def guardar_memoria():
    """Guarda la memoria actual en memoria.json."""

    with open(
        RUTA_MEMORIA,
        "w",
        encoding="utf-8"
    ) as archivo:
        json.dump(
            memoria,
            archivo,
            ensure_ascii=False,
            indent=4
        )


def guardar_proyecto(nombre_proyecto):
    """Guarda el nombre del proyecto y persiste el cambio."""

    memoria["proyecto_actual"] = nombre_proyecto
    guardar_memoria()


def obtener_proyecto():
    """Devuelve el nombre del proyecto guardado."""

    return memoria["proyecto_actual"]


def guardar_interaccion(solicitud, respuesta):
    """Guarda una solicitud y su respuesta en el historial."""

    interaccion = {
        "solicitud": str(solicitud),
        "respuesta": str(respuesta)
    }

    memoria["historial"].append(interaccion)
    guardar_memoria()


def obtener_historial():
    """Devuelve todas las interacciones almacenadas."""

    return memoria["historial"]


def construir_contexto(limite=5):
    """Construye el contexto usando las últimas interacciones."""

    historial = memoria["historial"]

    if not historial:
        return "No existen conversaciones anteriores."

    interacciones_recientes = historial[-limite:]
    contexto = ""

    for interaccion in interacciones_recientes:
        contexto += (
            "\nUsuario: "
            + str(interaccion["solicitud"])
            + "\nAgente: "
            + str(interaccion["respuesta"])
            + "\n"
        )

    return contexto
