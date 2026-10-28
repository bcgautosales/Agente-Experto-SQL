from io import BytesIO
from gtts import gTTS


def convertir_texto_a_voz(texto, idioma="es"):
    """Convierte el texto de SQL Nexus en audio en español."""
    if not texto or not texto.strip():
        return None

    audio = BytesIO()

    sintetizador = gTTS(
        text=texto,
        lang=idioma,
        slow=False
    )

    sintetizador.write_to_fp(audio)
    audio.seek(0)

    return audio.getvalue()
