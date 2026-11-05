
"""Base de datos SQLite para el historial de SQL Nexus."""

import sqlite3
from datetime import datetime
from pathlib import Path


# La base de datos se guarda junto a los archivos del proyecto.
BASE_DIR = Path(__file__).resolve().parent
RUTA_BD = BASE_DIR / "agente_historial.db"


def conectar():
    """Abre una conexión con la base de datos SQLite."""
    conexion = sqlite3.connect(RUTA_BD)
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_base_datos():
    """Crea la tabla del historial si todavía no existe."""
    with conectar() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS consultas_agente (
                id_consulta INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT NOT NULL,
                consulta TEXT NOT NULL,
                respuesta TEXT NOT NULL,
                origen TEXT NOT NULL,
                herramienta TEXT NOT NULL,
                uso_ia INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conexion.commit()


def registrar_consulta(
    consulta,
    respuesta,
    origen,
    herramienta
):
    """Guarda una consulta y la respuesta del agente."""
    crear_base_datos()

    uso_ia = 1 if str(origen).lower() == "gemini" else 0

    with conectar() as conexion:
        cursor = conexion.execute(
            """
            INSERT INTO consultas_agente (
                fecha_hora,
                consulta,
                respuesta,
                origen,
                herramienta,
                uso_ia
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(timespec="seconds"),
                str(consulta),
                str(respuesta),
                str(origen),
                str(herramienta),
                uso_ia,
            ),
        )
        conexion.commit()
        return cursor.lastrowid


def listar_consultas(limite=20):
    """Devuelve las consultas más recientes."""
    crear_base_datos()

    limite = max(1, min(int(limite), 1000))

    with conectar() as conexion:
        filas = conexion.execute(
            """
            SELECT
                id_consulta,
                fecha_hora,
                consulta,
                respuesta,
                origen,
                herramienta,
                uso_ia
            FROM consultas_agente
            ORDER BY id_consulta DESC
            LIMIT ?
            """,
            (limite,),
        ).fetchall()

    return [dict(fila) for fila in filas]


def obtener_resumen():
    """Calcula estadísticas generales del historial."""
    crear_base_datos()

    with conectar() as conexion:
        fila = conexion.execute(
            """
            SELECT
                COUNT(*) AS total,
                COALESCE(SUM(
                    CASE WHEN uso_ia = 0 THEN 1 ELSE 0 END
                ), 0) AS locales,
                COALESCE(SUM(
                    CASE WHEN uso_ia = 1 THEN 1 ELSE 0 END
                ), 0) AS gemini
            FROM consultas_agente
            """
        ).fetchone()

    return {
        "total": fila["total"],
        "locales": fila["locales"],
        "gemini": fila["gemini"],
    }


# Crea la base de datos y la tabla al importar este módulo.
crear_base_datos()
