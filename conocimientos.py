import json
import unicodedata
from pathlib import Path

RUTA_CONOCIMIENTOS = Path(__file__).resolve().parent / "conocimientos.json"


def normalizar(texto):
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )
    return " ".join(texto.split()).strip("¿?¡!.,;: ")


def cargar_conocimientos():
    """Carga los conocimientos desde el archivo JSON."""
    if not RUTA_CONOCIMIENTOS.exists():
        return []

    try:
        with open(RUTA_CONOCIMIENTOS, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            return datos if isinstance(datos, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def listar_conocimientos():
    """Devuelve todos los conocimientos guardados."""
    return cargar_conocimientos()



def guardar_conocimiento(pregunta, respuesta):
    """Guarda un conocimiento nuevo o actualiza uno existente."""
    pregunta = pregunta.strip()
    respuesta = respuesta.strip()

    if not pregunta or not respuesta:
        raise ValueError("La pregunta y la respuesta son obligatorias.")

    conocimientos = cargar_conocimientos()
    clave = normalizar(pregunta)
    actualizado = False

    for item in conocimientos:
        clave_existente = normalizar(
            item.get("pregunta") or item.get("concepto", "")
        )

        if clave_existente == clave:
            item["pregunta"] = pregunta
            item["respuesta"] = respuesta
            item.pop("concepto", None)
            actualizado = True
            break

    if not actualizado:
        conocimientos.append({
            "pregunta": pregunta,
            "respuesta": respuesta
        })

    temporal = RUTA_CONOCIMIENTOS.with_suffix(".tmp")

    with open(temporal, "w", encoding="utf-8") as archivo:
        json.dump(
            conocimientos,
            archivo,
            ensure_ascii=False,
            indent=4
        )

    temporal.replace(RUTA_CONOCIMIENTOS)

    return "actualizado" if actualizado else "guardado"



def eliminar_conocimiento(pregunta):
    """Elimina un conocimiento usando su pregunta."""
    conocimientos = cargar_conocimientos()
    clave = normalizar(pregunta)

    filtrados = [
        item for item in conocimientos
        if normalizar(item.get("pregunta") or item.get("concepto", "")) != clave
    ]

    if len(filtrados) == len(conocimientos):
        return False

    temporal = RUTA_CONOCIMIENTOS.with_suffix(".tmp")

    with open(temporal, "w", encoding="utf-8") as archivo:
        json.dump(
            filtrados,
            archivo,
            ensure_ascii=False,
            indent=4
        )

    temporal.replace(RUTA_CONOCIMIENTOS)
    return True


def buscar_conocimiento(pregunta):
    """Busca conocimientos personalizados para responder preguntas."""
    texto = normalizar(pregunta)
    conocimientos = cargar_conocimientos()

    # Primero busca una coincidencia exacta.
    for item in conocimientos:
        if normalizar(item.get("pregunta", "")) == texto:
            return item.get("respuesta", "")

    # Después busca si una pregunta guardada aparece en el mensaje.
    coincidencias = []

    for item in conocimientos:
        clave = normalizar(item.get("pregunta", ""))

        if len(clave) >= 5 and clave in texto:
            coincidencias.append(item)

    if coincidencias:
        mejor = max(
            coincidencias,
            key=lambda item: len(normalizar(item.get("pregunta", "")))
        )
        return mejor.get("respuesta", "")

    return None