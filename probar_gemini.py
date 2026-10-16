from google import genai
from google.genai import types
import os
import traceback

print("1. Iniciando prueba...", flush=True)

if not os.getenv("GEMINI_API_KEY"):
    print("ERROR: Falta GEMINI_API_KEY.", flush=True)
else:
    try:
        cliente = genai.Client(
            http_options=types.HttpOptions(
                timeout=90000
            )
        )

        print("2. Enviando pregunta a Gemini...", flush=True)

        respuesta = cliente.interactions.create(
            model="gemini-3.8-flash",
            input="Responde brevemente en español: ¿Qué es SQL?",
            generation_config={"thinking_level": "low"}
        )

        print("3. Respuesta recibida:", flush=True)
        print(repr(respuesta.output_text), flush=True)

    except Exception as error:
        print("4. La solicitud falló:", flush=True)
        print(type(error).__name__, flush=True)
        print(str(error), flush=True)
