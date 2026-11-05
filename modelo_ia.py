"""Conexión de SQL Nexus con Gemini mediante la API de Interactions."""

import os

from dotenv import load_dotenv
from google import genai
from prompt_sistema import PROMPT_SISTEMA

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "No se encontró GEMINI_API_KEY. Revisa el archivo .env."
    )

cliente = genai.Client(api_key=api_key)


def preguntar_ia(pregunta, contexto=""):
    mensaje = f"""
{PROMPT_SISTEMA}

CONTEXTO DE LA CONVERSACIÓN:
{contexto}

PREGUNTA DEL USUARIO:
{pregunta}

Responde de forma clara, educativa y organizada.
Si incluyes consultas SQL, explica qué hacen.
No inventes datos sobre la base de datos del usuario.
"""

    respuesta = cliente.interactions.create(
        model="gemini-3.1-flash-lite",
        input=mensaje,
    )

    texto = respuesta.output_text

    if not texto:
        raise RuntimeError("Gemini no devolvió una respuesta de texto.")

    return texto
