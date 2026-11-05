
"""Base de datos SQLite para el historial de SQL Nexus."""

import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RUTA_BD = BASE_DIR / "agente_historial.db"


def conectar():
    conexion = sqlite3.connect(RUTA_BD)
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_base_datos():
    """Crea la tabla y agrega columnas faltantes sin borrar datos."""
    with conectar() as conexion:
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS consultas_agente (
                id_consulta INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT NOT NULL,
                consulta TEXT NOT NULL,
                respuesta TEXT NOT NULL,
                origen TEXT NOT NULL,
                herramienta TEXT NOT NULL,
                uso_ia INTEGER NOT NULL DEFAULT 0,
                dominio TEXT,
                capacidad TEXT,
                aprendizaje_id TEXT,
                estado_aprendizaje TEXT NOT NULL DEFAULT 'no_aplica'
            )
        """)

        columnas = {
            fila["name"]
            for fila in conexion.execute(
                "PRAGMA table_info(consultas_agente)"
            ).fetchall()
        }

        nuevas_columnas = {
            "dominio": "TEXT",
            "capacidad": "TEXT",
            "aprendizaje_id": "TEXT",
            "estado_aprendizaje": (
                "TEXT NOT NULL DEFAULT 'no_aplica'"
            ),
        }

        for nombre, tipo in nuevas_columnas.items():
            if nombre not in columnas:
                conexion.execute(
                    f"ALTER TABLE consultas_agente "
                    f"ADD COLUMN {nombre} {tipo}"
                )

        # Conserva las consultas existentes y refleja su origen.
        conexion.execute("""
            UPDATE consultas_agente
            SET estado_aprendizaje = 'pendiente'
            WHERE LOWER(origen) = 'gemini'
              AND estado_aprendizaje = 'no_aplica'
        """)

        conexion.commit()


def registrar_consulta(consulta, respuesta, origen, herramienta):
    """Registra una consulta y devuelve su identificador."""
    crear_base_datos()

    origen_texto = str(origen)
    herramienta_texto = str(herramienta)
    uso_ia = int(origen_texto.strip().lower() == "gemini")
    estado = "pendiente" if uso_ia else "no_aplica"

    with conectar() as conexion:
        cursor = conexion.execute("""
            INSERT INTO consultas_agente (
                fecha_hora, consulta, respuesta, origen, herramienta,
                uso_ia, dominio, capacidad, estado_aprendizaje
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(timespec="seconds"),
            str(consulta),
            str(respuesta),
            origen_texto,
            herramienta_texto,
            uso_ia,
            "sql",
            herramienta_texto,
            estado,
        ))
        conexion.commit()
        return cursor.lastrowid


def actualizar_estado_aprendizaje_sql(
    id_consulta, estado, aprendizaje_id=None
):
    """Sincroniza en SQLite la decisión sobre una respuesta."""
    estados_validos = {
        "no_aplica", "pendiente", "aceptado", "rechazado"
    }
    if estado not in estados_validos:
        raise ValueError(f"Estado de aprendizaje no válido: {estado}")

    crear_base_datos()

    with conectar() as conexion:
        cursor = conexion.execute("""
            UPDATE consultas_agente
            SET estado_aprendizaje = ?, aprendizaje_id = ?
            WHERE id_consulta = ?
        """, (estado, aprendizaje_id, id_consulta))
        conexion.commit()
        return cursor.rowcount > 0


def listar_consultas(limite=20, dominio=None):
    """Devuelve las consultas más recientes, opcionalmente por dominio."""
    crear_base_datos()
    limite = max(1, min(int(limite), 1000))

    with conectar() as conexion:
        if dominio is None:
            filas = conexion.execute("""
                SELECT *
                FROM consultas_agente
                ORDER BY id_consulta DESC
                LIMIT ?
            """, (limite,)).fetchall()
        else:
            filas = conexion.execute("""
                SELECT *
                FROM consultas_agente
                WHERE dominio = ?
                ORDER BY id_consulta DESC
                LIMIT ?
            """, (dominio, limite)).fetchall()

    return [dict(fila) for fila in filas]


def obtener_resumen():
    """Calcula estadísticas del historial y del aprendizaje."""
    crear_base_datos()

    with conectar() as conexion:
        fila = conexion.execute("""
            SELECT
                COUNT(*) AS total,
                COALESCE(SUM(CASE WHEN uso_ia = 0 THEN 1 ELSE 0 END), 0)
                    AS locales,
                COALESCE(SUM(CASE WHEN uso_ia = 1 THEN 1 ELSE 0 END), 0)
                    AS gemini,
                COALESCE(SUM(CASE WHEN estado_aprendizaje = 'pendiente'
                    THEN 1 ELSE 0 END), 0) AS pendientes,
                COALESCE(SUM(CASE WHEN estado_aprendizaje = 'aceptado'
                    THEN 1 ELSE 0 END), 0) AS aceptados,
                COALESCE(SUM(CASE WHEN estado_aprendizaje = 'rechazado'
                    THEN 1 ELSE 0 END), 0) AS rechazados
            FROM consultas_agente
        """).fetchone()

    return dict(fila)


crear_base_datos()
