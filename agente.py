import re
import unicodedata

from conocimientos import buscar_conocimiento

"""
Agente experto en SQL con integración de Gemini.

Contiene funciones para responder preguntas sobre SQL,
generar consultas y apoyar tareas relacionadas con bases
de datos.
"""


def responder_pregunta(pregunta):
    """Responde preguntas SQL usando conocimientos guardados o locales."""

    # 1. Buscar primero los conocimientos agregados desde Alimentar.
    respuesta_guardada = buscar_conocimiento(pregunta)

    if respuesta_guardada:
        return respuesta_guardada

    # 2. Normalizar la pregunta para buscar en los conocimientos locales.
    def normalizar(texto):
        texto = texto.strip().lower()
        texto = unicodedata.normalize("NFD", texto)
        texto = "".join(
            caracter for caracter in texto
            if unicodedata.category(caracter) != "Mn"
        )
        texto = re.sub(r"[¿?¡!.,;:()]", " ", texto)
        texto = re.sub(r"\s+", " ", texto)
        return texto.strip()

    texto = normalizar(pregunta)

    # Los conocimientos agregados desde la sección "Alimentar" tienen prioridad.
    respuesta_personalizada = buscar_conocimiento(pregunta)
    if respuesta_personalizada:
        return respuesta_personalizada

    # Cada entrada contiene expresiones que puede utilizar el usuario
    # y una respuesta programada que no requiere conexión con Gemini.
    conocimientos = [
        # FUNDAMENTOS DE SQL
        (
            ["que es sql", "que significa sql", "definicion de sql"],
            "SQL significa Structured Query Language. Es un lenguaje "
            "utilizado para consultar, insertar, modificar y administrar "
            "datos en bases de datos relacionales."
        ),
        (
            ["que es una base de datos", "que son las bases de datos"],
            "Una base de datos es un conjunto organizado de información "
            "que puede almacenarse, consultarse y actualizarse mediante "
            "un sistema gestor de bases de datos."
        ),
        (
            ["que es un gestor de bases de datos", "que es un sgbd"],
            "Un SGBD es un sistema que permite crear, consultar, "
            "administrar y proteger bases de datos. Algunos ejemplos "
            "son PostgreSQL, MySQL, SQL Server y SQLite."
        ),
        (
            ["que es una tabla", "que es una tabla sql"],
            "Una tabla organiza los datos en filas y columnas. Cada "
            "columna representa un atributo y cada fila un registro."
        ),
        (
            ["que es una fila", "que es un registro en sql"],
            "Una fila o registro contiene los valores correspondientes "
            "a un elemento almacenado en una tabla."
        ),
        (
            ["que es una columna", "que es un campo en sql"],
            "Una columna representa un atributo de los datos, como "
            "nombre, correo, fecha de nacimiento o precio."
        ),
        (
            ["que es un esquema", "que es un schema"],
            "Un esquema organiza objetos de una base de datos, como "
            "tablas, vistas y funciones. Su comportamiento depende del "
            "sistema gestor utilizado."
        ),

        # CONSULTAS Y FILTRADO
        (
            ["que es select", "para que sirve select"],
            "SELECT permite consultar datos. Ejemplo:\n"
            "SELECT nombre, correo FROM usuarios;"
        ),
        (
            ["que es where", "para que sirve where"],
            "WHERE filtra filas según una condición. Ejemplo:\n"
            "SELECT * FROM productos WHERE precio > 100;"
        ),
        (
            ["que es order by", "para que sirve order by"],
            "ORDER BY ordena los resultados. ASC indica orden ascendente "
            "y DESC descendente. Ejemplo:\n"
            "SELECT * FROM productos ORDER BY precio DESC;"
        ),
        (
            ["que es distinct", "para que sirve distinct"],
            "DISTINCT elimina las combinaciones de valores duplicadas "
            "del resultado. Ejemplo:\n"
            "SELECT DISTINCT ciudad FROM usuarios;"
        ),
        (
            ["que es limit", "para que sirve limit"],
            "LIMIT restringe el número de filas devueltas en gestores "
            "que lo admiten, como PostgreSQL y MySQL. Ejemplo:\n"
            "SELECT * FROM productos LIMIT 10;\n"
            "En SQL Server suele utilizarse TOP o OFFSET/FETCH."
        ),
        (
            ["que es offset", "para que sirve offset"],
            "OFFSET permite omitir una cantidad de filas, normalmente "
            "para paginar resultados. Su sintaxis varía según el gestor."
        ),
        (
            ["que es like", "para que sirve like"],
            "LIKE compara texto con patrones. El símbolo % representa "
            "cero o más caracteres y _ representa un carácter. Ejemplo:\n"
            "SELECT * FROM usuarios WHERE nombre LIKE 'Ana%';"
        ),
        (
            ["que es in", "para que sirve in"],
            "IN comprueba si un valor coincide con alguno de una lista. "
            "Ejemplo:\n"
            "SELECT * FROM usuarios WHERE ciudad IN ('Bogota', 'Cali');"
        ),
        (
            ["que es between", "para que sirve between"],
            "BETWEEN comprueba si un valor está dentro de un intervalo "
            "incluyendo sus extremos. Ejemplo:\n"
            "SELECT * FROM productos WHERE precio BETWEEN 100 AND 500;"
        ),
        (
            ["que es and en sql", "que es el operador and"],
            "AND exige que ambas condiciones sean verdaderas. Ejemplo:\n"
            "SELECT * FROM productos "
            "WHERE precio > 100 AND stock > 0;"
        ),
        (
            ["que es or en sql", "que es el operador or"],
            "OR requiere que al menos una de las condiciones sea "
            "verdadera. Ejemplo:\n"
            "SELECT * FROM usuarios "
            "WHERE ciudad = 'Cali' OR ciudad = 'Bogota';"
        ),
        (
            ["que es not en sql", "que es el operador not"],
            "NOT niega una condición. Ejemplo:\n"
            "SELECT * FROM usuarios WHERE NOT ciudad = 'Cali';"
        ),

        # AGRUPACIONES Y FUNCIONES
        (
            ["que es group by", "para que sirve group by"],
            "GROUP BY agrupa filas con valores comunes, normalmente "
            "para calcular totales o promedios. Ejemplo:\n"
            "SELECT ciudad, COUNT(*) FROM usuarios GROUP BY ciudad;"
        ),
        (
            ["que es having", "para que sirve having"],
            "HAVING filtra grupos después de GROUP BY. Ejemplo:\n"
            "SELECT ciudad, COUNT(*) AS total FROM usuarios "
            "GROUP BY ciudad HAVING COUNT(*) > 5;"
        ),
        (
            ["que es count", "para que sirve count"],
            "COUNT cuenta filas o valores no NULL. COUNT(*) cuenta "
            "todas las filas del resultado. Ejemplo:\n"
            "SELECT COUNT(*) AS total FROM usuarios;"
        ),
        (
            ["que es sum", "para que sirve sum"],
            "SUM calcula la suma de los valores numéricos no NULL. "
            "Ejemplo:\n"
            "SELECT SUM(precio) AS total FROM productos;"
        ),
        (
            ["que es avg", "que es average", "para que sirve avg"],
            "AVG calcula el promedio de los valores numéricos no NULL. "
            "Ejemplo:\n"
            "SELECT AVG(precio) AS precio_promedio FROM productos;"
        ),
        (
            ["que es min", "para que sirve min"],
            "MIN devuelve el valor mínimo de una expresión. Ejemplo:\n"
            "SELECT MIN(precio) AS precio_minimo FROM productos;"
        ),
        (
            ["que es max", "para que sirve max"],
            "MAX devuelve el valor máximo de una expresión. Ejemplo:\n"
            "SELECT MAX(precio) AS precio_maximo FROM productos;"
        ),
        (
            ["que es coalesce", "para que sirve coalesce"],
            "COALESCE devuelve el primer argumento que no sea NULL. "
            "Ejemplo:\n"
            "SELECT COALESCE(telefono, 'Sin telefono') FROM usuarios;"
        ),

        # RELACIONES ENTRE TABLAS
        (
            ["que es una clave primaria", "que es primary key"],
            "PRIMARY KEY identifica de forma única cada fila. No permite "
            "claves duplicadas ni valores NULL. Puede estar formada "
            "por una o varias columnas."
        ),
        (
            ["que es una clave foranea", "que es foreign key"],
            "FOREIGN KEY relaciona una tabla con una clave de otra tabla "
            "o de la misma tabla. Ayuda a mantener la integridad "
            "referencial."
        ),
        (
            ["que es unique", "que es la restriccion unique"],
            "UNIQUE impide que se repitan determinadas combinaciones "
            "de valores en una tabla. El tratamiento de NULL depende "
            "del gestor de bases de datos."
        ),
        (
            ["que es not null", "para que sirve not null"],
            "NOT NULL obliga a que una columna tenga un valor y no "
            "permite que se almacene NULL en ella."
        ),
        (
            ["que es check", "para que sirve check"],
            "CHECK establece una condición que deben cumplir los valores "
            "de una fila. Ejemplo:\n"
            "edad INT CHECK (edad >= 18)\n"
            "La sintaxis exacta depende del gestor."
        ),
        (
            ["que es join", "para que sirve join"],
            "JOIN combina filas de tablas relacionadas mediante una "
            "condición de unión. Los tipos principales son INNER JOIN, "
            "LEFT JOIN, RIGHT JOIN y FULL OUTER JOIN."
        ),
        (
            [
                "que es inner join",
                "que es un inner join",
                "para que sirve inner join",
                "para que sirve un inner join",
                "explica inner join",
                "explicame inner join",
            ],
            "INNER JOIN devuelve las filas que tienen coincidencias "
            "según la condición de unión en ambas tablas. Ejemplo:\n"
            "SELECT u.nombre, p.id FROM usuarios u "
            "INNER JOIN pedidos p ON u.id = p.usuario_id;"
        ),
        (
            ["que es left join", "para que sirve left join"],
            "LEFT JOIN devuelve todas las filas de la tabla izquierda "
            "y las coincidencias de la derecha. Cuando no hay "
            "coincidencia, las columnas derechas contienen NULL."
        ),
        (
            ["que es right join", "para que sirve right join"],
            "RIGHT JOIN devuelve todas las filas de la tabla derecha "
            "y las coincidencias de la izquierda. Si no hay coincidencia, "
            "las columnas izquierdas contienen NULL."
        ),
        (
            ["que es full outer join", "para que sirve full outer join"],
            "FULL OUTER JOIN devuelve las filas coincidentes y también "
            "las filas sin coincidencia de ambas tablas. No todos los "
            "gestores lo admiten directamente."
        ),

        # MODIFICACIÓN Y ESTRUCTURA DE DATOS
        (
            ["que es insert", "que es insert into"],
            "INSERT INTO agrega nuevas filas a una tabla. Ejemplo:\n"
            "INSERT INTO usuarios (nombre, correo) "
            "VALUES ('Ana', 'ana@example.com');"
        ),
        (
            ["que es update", "para que sirve update"],
            "UPDATE modifica filas existentes. Usa WHERE para limitar "
            "las filas afectadas. Ejemplo:\n"
            "UPDATE productos SET precio = 150 WHERE id = 1;"
        ),
        (
            ["que es delete", "para que sirve delete"],
            "DELETE elimina filas de una tabla. Sin WHERE puede eliminar "
            "todas las filas, por lo que conviene revisar la condición "
            "antes de ejecutarlo. Ejemplo:\n"
            "DELETE FROM usuarios WHERE id = 5;"
        ),
        (
            ["que es create table", "para que sirve create table"],
            "CREATE TABLE crea una tabla y define sus columnas y "
            "restricciones. Ejemplo:\n"
            "CREATE TABLE usuarios (id INT PRIMARY KEY, nombre VARCHAR(100));"
        ),
        (
            ["que es alter table", "para que sirve alter table"],
            "ALTER TABLE modifica la estructura de una tabla, por "
            "ejemplo agregando una columna. La sintaxis varía según "
            "el gestor de bases de datos."
        ),
        (
            ["que es drop table", "para que sirve drop table"],
            "DROP TABLE elimina la definición de una tabla y sus datos. "
            "Es una operación potencialmente destructiva; verifica "
            "el nombre y las dependencias antes de usarla."
        ),
        (
            ["que es truncate", "que es truncate table"],
            "TRUNCATE TABLE elimina todas las filas de una tabla "
            "sin eliminar su estructura. Sus efectos sobre transacciones, "
            "identidades y restricciones dependen del gestor."
        ),

        # VALORES ESPECIALES Y CONSULTAS AVANZADAS
        (
            ["que es null", "que significa null en sql"],
            "NULL representa un valor ausente o desconocido. Para "
            "comprobarlo se usa IS NULL o IS NOT NULL, no una "
            "comparación normal con el signo igual."
        ),
        (
            ["que es una subconsulta", "que es subquery"],
            "Una subconsulta es una consulta SQL anidada dentro de otra. "
            "Puede utilizarse en WHERE, FROM, SELECT y otros contextos."
        ),
        (
            ["que es una vista", "que es view en sql"],
            "Una vista es una consulta guardada que se presenta como "
            "una tabla virtual. Ayuda a simplificar consultas y "
            "controlar qué información se expone."
        ),
        (
            ["que es un indice", "que es index en sql"],
            "Un índice ayuda al gestor a localizar filas con mayor "
            "rapidez en determinadas consultas. Puede ocupar espacio "
            "adicional y aumentar el costo de algunas modificaciones."
        ),
        (
            ["que es una transaccion", "que es transaction en sql"],
            "Una transacción agrupa operaciones que deben tratarse "
            "como una unidad lógica. COMMIT confirma los cambios y "
            "ROLLBACK revierte cambios no confirmados, según el gestor."
        ),
        (
            ["que es commit en sql", "para que sirve commit"],
            "COMMIT confirma los cambios de una transacción. Una vez "
            "confirmados, su reversión depende de las capacidades "
            "del gestor y de otras operaciones."
        ),
        (
            ["que es rollback", "para que sirve rollback"],
            "ROLLBACK revierte los cambios no confirmados de una "
            "transacción activa, cuando el gestor y el contexto "
            "transaccional lo permiten."
        ),
        (
            ["que es una union", "que es union en sql"],
            "UNION combina los resultados de dos consultas compatibles "
            "y elimina duplicados. UNION ALL conserva los duplicados."
        ),
        (
            ["que es una cte", "que es with en sql"],
            "Una CTE se define normalmente con WITH y permite dar nombre "
            "temporal al resultado de una consulta para reutilizarlo "
            "dentro de una sentencia."
        ),
        (
            ["que es una funcion agregada", "que son funciones agregadas"],
            "Las funciones agregadas calculan un resultado a partir de "
            "varias filas. Algunos ejemplos son COUNT, SUM, AVG, MIN "
            "y MAX."
        ),
        (
            ["que es una relacion uno a muchos", "relacion uno a muchos"],
            "Una relación uno a muchos ocurre cuando un registro de una "
            "tabla puede relacionarse con varios registros de otra. "
            "Suele representarse con una clave foránea en la tabla hija."
        ),
        (
            ["que es normalizacion de bases de datos",
                "que es normalizar una base de datos"],
            "La normalización organiza las tablas para reducir "
            "redundancias y anomalías de inserción, actualización y "
            "eliminación. Incluye formas normales como 1FN, 2FN y 3FN."
        ),

        # SEGURIDAD
        (
            ["que es sql injection", "que es inyeccion sql"],
            "La inyección SQL ocurre cuando entradas no confiables "
            "alteran una consulta construida de forma insegura. Para "
            "prevenirla, utiliza consultas parametrizadas, valida "
            "entradas y aplica el principio de mínimo privilegio."
        ),
        (
            ["que son consultas parametrizadas",
                "que es una consulta parametrizada"],
            "Las consultas parametrizadas separan el código SQL de los "
            "valores suministrados por el usuario. Son una defensa "
            "fundamental contra la inyección SQL."
        ),
        (
            ["que es grant en sql", "para que sirve grant"],
            "GRANT concede privilegios a un usuario o rol. Los permisos "
            "disponibles y su sintaxis dependen del gestor."
        ),
        (
            ["que es revoke en sql", "para que sirve revoke"],
            "REVOKE retira privilegios previamente concedidos. Debe "
            "usarse para mantener los permisos ajustados a las "
            "necesidades de cada usuario o rol."
        ),
    ]

    # Primero busca expresiones específicas y luego las más generales.
    # Así se priorizan términos como INNER JOIN frente a JOIN.
    conocimientos.sort(
        key=lambda elemento: max(
            len(normalizar(alias)) for alias in elemento[0]
        ),
        reverse=True
    )

    for preguntas, respuesta in conocimientos:
        for variante in preguntas:
            variante_normalizada = normalizar(variante)

            # Acepta la pregunta exacta o cuando el concepto aparece
            # dentro de una pregunta más larga.
            if (
                texto == variante_normalizada
                or variante_normalizada in texto
            ):
                return respuesta

    # Esta respuesta indica que el conocimiento local no fue suficiente.
    # En el siguiente paso conectaremos esta situación con el respaldo
    # de Gemini desde el flujo principal del agente.
    return (
        "No encontré una respuesta local para esa pregunta. "
        "Puedo responder conceptos de SQL, consultas, filtros, "
        "uniones, funciones, restricciones, transacciones y seguridad. "
        "Intenta formular la pregunta con el nombre del concepto SQL."
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
    """Selecciona la herramienta adecuada para la solicitud."""

    texto = solicitud.lower()

    # Consultar el estado guardado del proyecto.
    if (
        "qué sabes de mi proyecto" in texto
        or "que sabes de mi proyecto" in texto
        or "qué sabes actualmente de mi proyecto" in texto
        or "que sabes actualmente de mi proyecto" in texto
        or "mostrar estado del proyecto" in texto
        or "muestra el estado del proyecto" in texto
        or "resumen del proyecto" in texto
        or "información del proyecto" in texto
        or "informacion del proyecto" in texto
    ):
        return "estado"

    # Mantén aquí tus condiciones actuales para:
    # ensenar, generar_sql y revisar_sql.
    # Conserva también el return final que ya tienes.
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
