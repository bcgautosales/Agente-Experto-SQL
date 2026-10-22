import os
from google import genai

from prompt_sistema import PROMPT_SISTEMA

cliente = genai.Client()


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
