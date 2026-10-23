"""
Memoria persistente del Agente Experto en SQL.
Guarda conversaciones y detecta el proyecto actual.
"""

import copy
import json
import os


RUTA_MEMORIA = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "memoria.json",
)

MEMORIA_INICIAL = {
    "proyecto_actual": None,
    "historial": [],
}


def cargar_memoria():
    """Carga la memoria guardada o crea una estructura inicial."""
    if os.path.exists(RUTA_MEMORIA):
        try:
            with open(RUTA_MEMORIA, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)

            if (
                isinstance(datos, dict)
                and isinstance(datos.get("historial"), list)
            ):
                datos.setdefault("proyecto_actual", None)
                return datos

        except (json.JSONDecodeError, OSError):
            pass

    return copy.deepcopy(MEMORIA_INICIAL)


memoria = cargar_memoria()


def guardar_memoria():
    """Guarda la memoria actual en el archivo JSON."""
    with open(RUTA_MEMORIA, "w", encoding="utf-8") as archivo:
        json.dump(
            memoria,
            archivo,
            ensure_ascii=False,
            indent=4,
        )


def guardar_proyecto(nombre_proyecto):
    """Guarda el proyecto actual y persiste el cambio."""
    nombre = str(nombre_proyecto).strip()

    if nombre:
        memoria["proyecto_actual"] = nombre
        guardar_memoria()


def obtener_proyecto():
    """Devuelve el proyecto actual guardado."""
    return memoria["proyecto_actual"]


def guardar_interaccion(solicitud, respuesta):
    """Añade una interacción al historial persistente."""
    memoria["historial"].append({
        "solicitud": str(solicitud),
        "respuesta": str(respuesta),
    })
    guardar_memoria()


def obtener_historial():
    """Devuelve el historial completo."""
    return memoria["historial"]


def detectar_proyecto(solicitud):
    """Detecta y guarda una descripción de proyecto SQL."""
    texto = solicitud.strip()
    texto_minuscula = texto.lower()

    expresiones = (
        "estoy desarrollando ",
        "estoy diseñando ",
        "estoy construyendo ",
        "estoy creando ",
        "mi proyecto es ",
        "mi proyecto consiste en ",
        "estoy trabajando en ",
    )

    for expresion in expresiones:
        posicion = texto_minuscula.find(expresion)

        if posicion == -1:
            continue

        proyecto = texto[
            posicion + len(expresion):
        ].strip()

        # Conservamos la descripción útil del proyecto.
        # Solo quitamos el final de la oración.
        proyecto = proyecto.split("\n", 1)[0]
        proyecto = proyecto.split(".", 1)[0]
        proyecto = proyecto.split(";", 1)[0]
        proyecto = proyecto.strip(" ,")

        if proyecto.lower().startswith("un "):
            proyecto = proyecto[3:].strip()
        elif proyecto.lower().startswith("una "):
            proyecto = proyecto[4:].strip()

        if proyecto:
            guardar_proyecto(proyecto)
            return proyecto

    return None


def construir_contexto(limite=5):
    """Construye contexto con el proyecto y conversaciones recientes."""
    contexto = ""
    proyecto_actual = obtener_proyecto()
    historial = obtener_historial()

    if proyecto_actual:
        contexto += (
            "\nPROYECTO ACTUAL:\n"
            + proyecto_actual
            + "\n"
        )

    if historial:
        interacciones = historial[-limite:]

        for interaccion in interacciones:
            contexto += (
                "\nUsuario: "
                + str(interaccion.get("solicitud", ""))
                + "\nAgente: "
                + str(interaccion.get("respuesta", ""))
                + "\n"
            )

    if not contexto:
        return "No existen conversaciones anteriores."

    return contexto
