
"""
Estado estructurado del proyecto del Agente Experto en SQL.
Organiza los datos importantes de cada proyecto.
"""

from memoria_agente import (
    memoria,
    guardar_memoria,
    obtener_proyecto,
)


def inicializar_estado_proyecto():
    """Crea la ficha estructurada si todavía no existe."""
    if "datos_proyecto" not in memoria:
        memoria["datos_proyecto"] = {
            "nombre": None,
            "tipo": None,
            "componentes": [],
            "tecnologias": [],
            "estado": "en definición",
        }
        guardar_memoria()

    return memoria["datos_proyecto"]


def sincronizar_nombre_proyecto():
    """Sincroniza el nombre detectado con la ficha del proyecto."""
    datos = inicializar_estado_proyecto()
    proyecto_actual = obtener_proyecto()

    if proyecto_actual:
        datos["nombre"] = proyecto_actual
        guardar_memoria()

    return datos


def registrar_componente(componente):
    """Registra un componente sin duplicarlo."""
    datos = inicializar_estado_proyecto()

    if componente not in datos["componentes"]:
        datos["componentes"].append(componente)
        guardar_memoria()


def registrar_tecnologia(tecnologia):
    """Registra una tecnología sin duplicarla."""
    datos = inicializar_estado_proyecto()

    if tecnologia not in datos["tecnologias"]:
        datos["tecnologias"].append(tecnologia)
        guardar_memoria()


def actualizar_estado_desde_solicitud(solicitud):
    """Extrae información técnica de una solicitud del usuario."""
    datos = sincronizar_nombre_proyecto()
    texto = solicitud.lower()

    componentes = {
        "base de datos": (
            "base de datos",
            "bases de datos",
            "bd",
            "mysql",
            "postgresql",
            "sqlite",
            "sql server",
        ),
        "consultas SQL": (
            "consulta sql",
            "consultas sql",
            "select",
            "where",
            "join",
            "insert into",
            "update ",
            "delete from",
        ),
        "diseño de tablas": (
            "tabla",
            "tablas",
            "columnas",
            "campos",
            "clave primaria",
            "clave foránea",
            "clave foranea",
        ),
        "relaciones": (
            "relación",
            "relaciones",
            "relacion",
            "relacionar tablas",
        ),
        "seguridad SQL": (
            "seguridad",
            "inyección sql",
            "inyeccion sql",
            "consultas parametrizadas",
            "permisos de base de datos",
        ),
        "optimización": (
            "optimizar",
            "optimización",
            "optimizacion",
            "índice",
            "indices",
            "índices",
            "rendimiento",
        ),
        "aplicación web": (
            "aplicación web",
            "aplicacion web",
            "sitio web",
            "página web",
            "pagina web",
        ),
        "integración": (
            "api",
            "integración",
            "integracion",
            "conectar la aplicación",
        ),
    }

    for componente, palabras in componentes.items():
        if any(palabra in texto for palabra in palabras):
            registrar_componente(componente)

    tecnologias = {
        "python": "Python",
        "mysql": "MySQL",
        "postgresql": "PostgreSQL",
        "sqlite": "SQLite",
        "sql server": "SQL Server",
        "mariadb": "MariaDB",
        "oracle": "Oracle Database",
        "fastapi": "FastAPI",
        "django": "Django",
        "flask": "Flask",
        "javascript": "JavaScript",
        "java": "Java",
        "node.js": "Node.js",
    }

    for palabra, tecnologia in tecnologias.items():
        if palabra in texto:
            registrar_tecnologia(tecnologia)

    tipos = {
        "aplicación web": "Aplicación web",
        "aplicacion web": "Aplicación web",
        "sistema de información": "Sistema de información",
        "sistema de informacion": "Sistema de información",
        "base de datos": "Base de datos",
        "sistema de gestión": "Sistema de gestión de datos",
        "sistema de gestion": "Sistema de gestión de datos",
        "inventario": "Sistema de gestión de inventario",
    }

    for expresion, tipo in tipos.items():
        if expresion in texto:
            datos["tipo"] = tipo
            guardar_memoria()
            break

    if "en desarrollo" in texto:
        datos["estado"] = "en desarrollo"
        guardar_memoria()
    elif "en pruebas" in texto:
        datos["estado"] = "en pruebas"
        guardar_memoria()
    elif (
        "proyecto terminado" in texto
        or "proyecto finalizado" in texto
    ):
        datos["estado"] = "finalizado"
        guardar_memoria()

    return datos


def obtener_estado_proyecto():
    """Devuelve la ficha estructurada actualizada."""
    return sincronizar_nombre_proyecto()


def construir_resumen_proyecto():
    """Genera un resumen legible de la ficha del proyecto."""
    datos = obtener_estado_proyecto()

    nombre = datos["nombre"] or "No definido"
    tipo = datos["tipo"] or "No definido"

    componentes = datos["componentes"]
    tecnologias = datos["tecnologias"]

    texto_componentes = (
        ", ".join(componentes)
        if componentes
        else "Aún no se han identificado componentes."
    )

    texto_tecnologias = (
        ", ".join(tecnologias)
        if tecnologias
        else "Aún no se han definido tecnologías."
    )

    return "\n".join([
        "FICHA DEL PROYECTO SQL",
        "======================",
        "",
        f"Nombre: {nombre}",
        f"Tipo de solución: {tipo}",
        f"Componentes: {texto_componentes}",
        f"Tecnologías: {texto_tecnologias}",
        f"Estado: {datos['estado']}",
    ])
