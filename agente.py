"""Agente experto en SQL con respuestas locales y conexión a Gemini."""

import os
import time
import unicodedata

from google import genai
from google.genai import types


MODELO_GEMINI = "gemini-3.8-flash"


def normalizar_texto(texto):
    """Convierte el texto a minúsculas y elimina los acentos."""
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFD", texto)

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    return texto.replace("¿", "").replace("?", "").strip()


def consultar_gemini(instruccion):
    """Envía una solicitud a Gemini y devuelve su respuesta."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return (
            "Error: falta configurar GEMINI_API_KEY. "
            "Configura la clave en PowerShell."
        )

    try:
        cliente = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=20000)
        )
    except Exception as error:
        return (
            f"Error al inicializar Gemini: "
            f"{type(error).__name__}: {error}"
        )

    for intento in range(2):
        try:
            respuesta = cliente.interactions.create(
                model=MODELO_GEMINI,
                input=instruccion,
                generation_config={"thinking_level": "low"}
            )

            texto = respuesta.output_text

            if texto and texto.strip():
                return texto.strip()

            return "Gemini no devolvió una respuesta de texto."

        except Exception as error:
            mensaje = str(error).lower()

            error_temporal = any(
                indicador in mensaje
                for indicador in (
                    "503",
                    "429",
                    "500",
                    "502",
                    "504",
                    "timeout",
                    "timed out",
                    "high demand",
                    "service_unavailable",
                    "resource_exhausted"
                )
            )

            if error_temporal and intento == 0:
                print(
                    "Gemini está temporalmente ocupado. "
                    "Reintentando una vez..."
                )
                time.sleep(2)
                continue

            return (
                f"Error al consultar Gemini: "
                f"{type(error).__name__}: {error}"
            )

    return "No se pudo completar la consulta a Gemini."


def responder_pregunta(pregunta):
    """Responde preguntas de SQL localmente o mediante Gemini."""

    if not pregunta.strip():
        return "Escribe una pregunta sobre SQL."

    texto = normalizar_texto(pregunta)

    respuestas = {
        "que es sql": (
            "SQL significa Structured Query Language. Es un lenguaje "
            "utilizado para consultar, insertar, actualizar y eliminar "
            "datos, así como administrar bases de datos relacionales."
        ),
        "que es select": (
            "SELECT permite consultar datos de una o varias tablas."
        ),
        "que es where": (
            "WHERE filtra las filas que cumplen una condición."
        ),
        "que es order by": (
            "ORDER BY ordena los resultados. ASC indica orden "
            "ascendente y DESC indica orden descendente."
        ),
        "que es group by": (
            "GROUP BY agrupa filas que comparten valores. Se utiliza "
            "frecuentemente con COUNT, SUM y AVG."
        ),
        "que es having": (
            "HAVING filtra grupos después de GROUP BY, mientras que "
            "WHERE filtra filas antes de la agrupación."
        ),
        "que es join": (
            "JOIN combina filas de dos o más tablas mediante "
            "una condición de relación."
        ),
        "que es inner join": (
            "INNER JOIN devuelve las filas que cumplen la condición "
            "de unión en ambas tablas."
        ),
        "que es left join": (
            "LEFT JOIN devuelve todas las filas de la tabla izquierda "
            "y las coincidencias de la derecha. Cuando no hay "
            "coincidencia, las columnas derechas contienen NULL."
        ),
        "que es una clave primaria": (
            "PRIMARY KEY identifica de forma única cada fila de una "
            "tabla. No permite duplicados ni valores NULL."
        ),
        "que es primary key": (
            "PRIMARY KEY identifica de forma única cada fila de una "
            "tabla. No permite duplicados ni valores NULL."
        ),
        "que es una clave foranea": (
            "FOREIGN KEY relaciona tablas y ayuda a mantener "
            "la integridad referencial."
        ),
        "que es foreign key": (
            "FOREIGN KEY relaciona tablas y ayuda a mantener "
            "la integridad referencial."
        ),
        "que es count": (
            "COUNT cuenta filas o valores no NULL. COUNT(*) cuenta "
            "todas las filas del resultado."
        ),
        "que es sum": (
            "SUM calcula la suma de los valores numéricos, "
            "ignorando los valores NULL."
        ),
        "que es avg": (
            "AVG calcula el promedio de los valores no NULL "
            "de una expresión numérica."
        ),
        "que es insert": (
            "INSERT INTO permite agregar nuevas filas a una tabla."
        ),
        "que es update": (
            "UPDATE modifica filas existentes. Usa WHERE para limitar "
            "las filas que deseas modificar."
        ),
        "que es delete": (
            "DELETE elimina filas de una tabla. Sin WHERE, puede "
            "eliminar todas sus filas."
        ),
        "que es null": (
            "NULL representa un valor ausente o desconocido. "
            "Se comprueba mediante IS NULL o IS NOT NULL."
        ),
        "que es una subconsulta": (
            "Una subconsulta es una consulta SQL anidada dentro "
            "de otra consulta."
        ),
        "que es una cte": (
            "Una CTE, o expresión de tabla común, se define mediante "
            "WITH y permite organizar una consulta en bloques con "
            "nombre. También puede utilizarse para consultas recursivas."
        ),
        "que es una subconsulta correlacionada": (
            "Una subconsulta correlacionada hace referencia a columnas "
            "de la consulta externa. Su resultado depende de esas "
            "columnas, aunque el optimizador puede transformar "
            "su ejecución para mejorar el rendimiento."
        ),
        "que es distinct": (
            "DISTINCT elimina las filas duplicadas del resultado."
        ),
        "que es create table": (
            "CREATE TABLE crea una tabla y define sus columnas "
            "y restricciones."
        )
    }
    # Primero intentamos responder con el diccionario local.
    if texto in respuestas:
        return respuestas[texto]

    instruccion = f"""
Eres un experto en SQL y bases de datos.

Responde en español de manera clara, completa y técnicamente precisa.
Incluye ejemplos SQL cuando sean útiles.
Explica diferencias entre motores de bases de datos cuando corresponda.
No inventes estructuras de tablas ni afirmes haber ejecutado consultas.

Pregunta del usuario:
{pregunta}
"""

    return consultar_gemini(instruccion)


def generar_consulta_sql(solicitud):
    """Genera consultas SQL a partir de solicitudes en lenguaje natural."""

    if not solicitud.strip():
        return "Describe la consulta SQL que necesitas."

    instruccion = f"""
Eres un experto en SQL, bases de datos y optimización.

Genera una consulta SQL que resuelva la solicitud del usuario.

Instrucciones:
- Responde en español.
- Presenta la consulta dentro de un bloque de código SQL.
- Explica brevemente cómo funciona.
- Si faltan nombres de tablas o columnas, indica tus suposiciones.
- No afirmes que ejecutaste o verificaste la consulta.
- Utiliza SQL estándar cuando sea posible.
- Advierte sobre operaciones que modifiquen o eliminen datos.
- Para conteos de relaciones, considera si corresponde LEFT JOIN
  o INNER JOIN.
- Si falta información imprescindible, solicita el esquema necesario.

Solicitud:
{solicitud}
"""

    return consultar_gemini(instruccion)
