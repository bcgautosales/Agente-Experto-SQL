"""
Agente experto en SQL con integración de Gemini.

Contiene funciones para responder preguntas sobre SQL,
generar consultas y apoyar tareas relacionadas con bases
de datos.
"""


def responder_pregunta(pregunta):
    """Responde preguntas sobre conceptos fundamentales de SQL."""

    pregunta_normalizada = pregunta.strip().lower()

    # Normalizar vocales acentuadas y signos de interrogacion.
    tabla_acentos = str.maketrans(
        "áéíóú",
        "aeiou"
    )

    pregunta_normalizada = pregunta_normalizada.translate(
        tabla_acentos
    )

    pregunta_normalizada = (
        pregunta_normalizada
        .replace("¿", "")
        .replace("?", "")
        .strip()
    )

    conocimientos = {
        "que es sql": (
            "SQL significa Structured Query Language. "
            "Es un lenguaje para consultar y administrar "
            "datos en bases de datos relacionales."
        ),

        "que es una clave primaria": (
            "PRIMARY KEY identifica de forma unica cada fila "
            "de una tabla. No permite valores duplicados ni NULL."
        ),

        "que es una clave foranea": (
            "FOREIGN KEY relaciona tablas y ayuda a mantener "
            "la integridad referencial."
        ),

        "que es select": (
            "SELECT permite consultar datos de una o varias tablas."
        ),

        "que es where": (
            "WHERE filtra filas segun una condicion."
        ),

        "que es order by": (
            "ORDER BY ordena los resultados de una consulta. "
            "ASC ordena de forma ascendente y DESC descendente."
        ),

        "que es group by": (
            "GROUP BY agrupa filas con valores comunes. "
            "Se utiliza frecuentemente con COUNT, SUM y AVG."
        ),

        "que es having": (
            "HAVING filtra grupos despues de aplicar GROUP BY. "
            "WHERE filtra filas antes de la agrupacion."
        ),

        "que es join": (
            "JOIN combina filas de dos o mas tablas mediante "
            "una condicion de relacion."
        ),

        "que es inner join": (
            "INNER JOIN devuelve las filas que cumplen la "
            "condicion de union en ambas tablas."
        ),

        "que es left join": (
            "LEFT JOIN devuelve todas las filas de la tabla "
            "izquierda y las coincidencias de la tabla derecha. "
            "Si no hay coincidencia, las columnas derechas "
            "contienen NULL."
        ),

        "que es count": (
            "COUNT cuenta filas o valores no NULL, segun la "
            "expresion utilizada. COUNT(*) cuenta todas las filas."
        ),

        "que es sum": (
            "SUM calcula la suma de los valores de una columna "
            "numerica, ignorando los valores NULL."
        ),

        "que es avg": (
            "AVG calcula el promedio de los valores no NULL "
            "de una expresion numerica."
        ),

        "que es insert": (
            "INSERT INTO agrega nuevas filas a una tabla."
        ),

        "que es update": (
            "UPDATE modifica filas existentes. Utiliza WHERE "
            "para limitar las filas afectadas cuando sea necesario."
        ),

        "que es delete": (
            "DELETE elimina filas de una tabla. Sin WHERE, "
            "puede eliminar todas las filas."
        ),

        "que es null": (
            "NULL representa un valor ausente o desconocido. "
            "Para comprobarlo normalmente se utiliza IS NULL "
            "o IS NOT NULL."
        ),

        "que es una subconsulta": (
            "Una subconsulta es una consulta SQL anidada dentro "
            "de otra consulta."
        ),

        "que es distinct": (
            "DISTINCT elimina las filas duplicadas del conjunto "
            "de resultados de una consulta."
        ),

        "que es create table": (
            "CREATE TABLE crea una tabla y define sus columnas "
            "y restricciones."
        )
    }

    # Buscar una coincidencia exacta.
    if pregunta_normalizada in conocimientos:
        return conocimientos[pregunta_normalizada]

    # Reconocer preguntas formuladas de otras maneras.
    for concepto, respuesta in conocimientos.items():
        nombre = concepto.replace("que es ", "")

        if nombre in pregunta_normalizada:
            return respuesta

    return (
        "Todavia no tengo una respuesta programada para esa "
        "pregunta. Intenta preguntar por SELECT, WHERE, JOIN, "
        "GROUP BY, HAVING, COUNT, INSERT, UPDATE o DELETE."
    )


def generar_consulta_sql(solicitud):
    """Genera consultas SQL mediante reglas predefinidas."""

    solicitud = solicitud.strip().lower()

    # Normalizar acentos.
    tabla_acentos = str.maketrans(
        "áéíóú",
        "aeiou"
    )
    solicitud = solicitud.translate(tabla_acentos)

    # Reconocer diferentes formas de solicitar consultas.
    if (
        "usuario" in solicitud
        and any(palabra in solicitud for palabra in [
            "todos", "mostrar", "listar", "ver", "consultar"
        ])
        and "activo" not in solicitud
    ):
        return (
            "SELECT *\n"
            "FROM usuarios;"
        )

    if (
        "producto" in solicitud
        and any(palabra in solicitud for palabra in [
            "todos", "mostrar", "listar", "ver", "consultar"
        ])
    ):
        return (
            "SELECT *\n"
            "FROM productos;"
        )

    if "usuario" in solicitud and "activo" in solicitud:
        return (
            "SELECT *\n"
            "FROM usuarios\n"
            "WHERE estado = 'activo';"
        )

    if (
        "usuario" in solicitud
        and any(palabra in solicitud for palabra in [
            "contar", "cantidad", "cuantos", "cuantas", "total"
        ])
    ):
        return (
            "SELECT COUNT(*) AS total_usuarios\n"
            "FROM usuarios;"
        )

    if (
        "usuario" in solicitud
        and "ordenar" in solicitud
        and "nombre" in solicitud
    ):
        return (
            "SELECT *\n"
            "FROM usuarios\n"
            "ORDER BY nombre ASC;"
        )

    if (
        "producto" in solicitud
        and any(palabra in solicitud for palabra in [
            "barato", "baratos", "economico", "economicos"
        ])
    ):
        return (
            "SELECT *\n"
            "FROM productos\n"
            "WHERE precio < 100;"
        )

    if (
        "producto" in solicitud
        and any(palabra in solicitud for palabra in [
            "caro", "caros", "costoso", "costosos"
        ])
    ):
        return (
            "SELECT *\n"
            "FROM productos\n"
            "ORDER BY precio DESC;"
        )

    return (
        "No reconozco esa solicitud todavia. "
        "Prueba con usuarios, productos, usuarios activos, "
        "contar usuarios, ordenar usuarios por nombre, "
        "productos baratos o productos caros."
    )


def integrar_arquitectura(nombre_proyecto):
    """Describe cómo se conectan los componentes de una solución SQL."""

    return "\n".join([
        f"INTEGRACIÓN DEL PROYECTO: {nombre_proyecto}",
        "========================================",
        "",
        "1. APLICACIÓN WEB O MÓVIL",
        "   Interfaz utilizada por el usuario.",
        "",
        "2. API",
        "   Recibe solicitudes y comunica los componentes.",
        "",
        "3. BACKEND",
        "   Procesa la lógica de negocio.",
        "",
        "4. BASE DE DATOS",
        "   Almacena la información estructurada.",
        "",
        "5. SQL",
        "   Permite consultar y administrar los datos.",
        "",
        "6. SEGURIDAD",
        "   Controla permisos y protege la información.",
        "",
        "FLUJO GENERAL",
        "WEB / MÓVIL -> API -> BACKEND -> BASE DE DATOS",
        "SQL se utiliza desde el backend para trabajar con los datos."
    ])


def decidir_herramienta(solicitud):
    """Selecciona la herramienta adecuada para una solicitud SQL."""

    texto = solicitud.strip().lower()

    # Preguntas sobre conceptos y definiciones de SQL.
    if any(palabra in texto for palabra in [
        "que es", "qué es", "explica", "explicame",
        "explícame", "ensen", "enseñ", "que significa",
        "qué significa", "diferencia entre", "para que sirve",
        "para qué sirve"
    ]):
        return "ensenar"

    # Solicitudes para crear o generar consultas SQL.
    elif any(palabra in texto for palabra in [
        "consulta sql", "generar consulta", "genera una consulta",
        "escribe una consulta", "crear consulta", "crea una consulta",
        "query", "select", "insert", "update", "delete",
        "mostrar usuarios", "listar usuarios", "contar usuarios",
        "mostrar productos", "listar productos"
    ]):
        return "generar_sql"

    # Solicitudes de revisión o mejora de consultas.
    elif any(palabra in texto for palabra in [
        "validar consulta", "revisar consulta", "corrige mi sql",
        "corregir consulta", "optimizar consulta", "mejorar consulta",
        "error en mi consulta", "esta consulta está bien"
    ]):
        return "revisar_sql"

    # Preguntas no reconocidas: se delegan a Gemini.
    else:
        return "ia"


def detectar_componente(solicitud):
    """Identifica el concepto SQL mencionado en la solicitud."""

    texto = solicitud.strip().lower()

    conceptos_sql = {
        "clave primaria": [
            "clave primaria", "primary key"
        ],
        "clave foranea": [
            "clave foranea", "clave foránea", "foreign key"
        ],
        "select": ["select"],
        "where": ["where"],
        "order by": ["order by"],
        "group by": ["group by"],
        "having": ["having"],
        "inner join": ["inner join"],
        "left join": ["left join"],
        "join": ["join"],
        "count": ["count"],
        "sum": ["sum"],
        "avg": ["avg", "average"],
        "insert": ["insert", "insert into"],
        "update": ["update"],
        "delete": ["delete"],
        "subconsulta": ["subconsulta", "subquery"],
        "distinct": ["distinct"],
        "create table": ["create table"],
        "base de datos": ["base de datos", "bases de datos"],
        "sql": ["sql"]
    }

    # Priorizar expresiones específicas antes de las generales.
    for concepto, palabras in conceptos_sql.items():
        if any(palabra in texto for palabra in palabras):
            return concepto

    return None
