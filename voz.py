
import asyncio
import re
from io import BytesIO

import edge_tts


VOZ_SQL_NEXUS = "es-CO-SalomeNeural"


async def _generar_audio(texto):
    """Genera audio natural con la voz colombiana de SQL Nexus."""

    audio = BytesIO()

    sintetizador = edge_tts.Communicate(
        text=texto,
        voice=VOZ_SQL_NEXUS,
        rate="+3%",
    )

    async for fragmento in sintetizador.stream():
        if fragmento["type"] == "audio":
            audio.write(fragmento["data"])

    audio.seek(0)
    return audio.getvalue()


def convertir_texto_a_voz(texto, idioma="es"):
    """Convierte la respuesta de SQL Nexus en audio hablado."""

    if not texto or not texto.strip():
        return None

    # Reducir saltos de línea y espacios repetidos.
    texto_limpio = re.sub(r"\n+", ". ", texto)
    texto_limpio = re.sub(r"\s+", " ", texto_limpio).strip()

    # Evitar pausas demasiado marcadas por puntuación repetida.
    texto_limpio = re.sub(r"\.{2,}", ".", texto_limpio)
    texto_limpio = re.sub(r",+", ",", texto_limpio)

    try:
        return asyncio.run(_generar_audio(texto_limpio))
    except Exception as error:
        print(f"Error al generar la voz de SQL Nexus: {error}")
        return None
