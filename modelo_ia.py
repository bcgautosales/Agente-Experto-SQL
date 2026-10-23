"""
Conexión del agente experto en SQL con Gemini.
"""

import os

from dotenv import load_dotenv
from google import genai
from prompt_sistema import PROMPT_SISTEMA

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "No se encontró GEMINI_API_KEY. "
        "Revisa el archivo .env."
    )

cliente = genai.Client(api_key=api_key)


def preguntar_ia(pregunta, contexto=""):
    """Envía una pregunta a Gemini con instrucciones y contexto."""

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

    respuesta = cliente.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=mensaje
    )

    return respuesta.text
