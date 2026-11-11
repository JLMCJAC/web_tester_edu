"""Módulo de Persistencia de Datos con SQLite y Purga Total con VACUUM (v1.4.2)."""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any

DB_PATH = Path(__file__).resolve().parent / "history.db"


def get_connection() -> sqlite3.Connection:
    """Establece conexión con la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Inicializa y migra el esquema de tablas para asegurar compatibilidad."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Tabla de Historial
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                target_url TEXT NOT NULL,
                engine_name TEXT NOT NULL,
                device_name TEXT NOT NULL
            )
        """)

        # Tabla de Favoritos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                target_url TEXT NOT NULL,
                category TEXT NOT NULL
            )
        """)

        # Tabla de Evidencias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                project_name TEXT NOT NULL,
                target_url TEXT NOT NULL,
                engine_name TEXT NOT NULL,
                device_name TEXT NOT NULL,
                findings TEXT NOT NULL
            )
        """)

        # Adaptación dinámica de columnas
        cursor.execute("PRAGMA table_info(evidences)")
        existing_cols = [col["name"] for col in cursor.fetchall()]

        if "author_name" not in existing_cols and "author" not in existing_cols:
            cursor.execute("ALTER TABLE evidences ADD COLUMN author_name TEXT DEFAULT ''")

        if "screenshot_path" not in existing_cols:
            cursor.execute("ALTER TABLE evidences ADD COLUMN screenshot_path TEXT DEFAULT ''")

        # Tabla de Perfiles Custom
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                user_agent TEXT DEFAULT ''
            )
        """)

        conn.commit()


# Inicializar base de datos al importar el módulo
init_db()


def save_test_record(target_url: str, engine_name: str, device_name: str) -> None:
    """Guarda un registro de prueba en el historial."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO test_history (timestamp, target_url, engine_name, device_name) VALUES (?, ?, ?, ?)",
            (timestamp, target_url, engine_name, device_name),
        )
        conn.commit()


def get_test_history(limit: int = 100) -> List[Dict[str, Any]]:
    """Obtiene el historial de pruebas."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM test_history ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]


def save_favorite(name: str, target_url: str, category: str = "General") -> None:
    """Guarda un marcador favorito."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO favorites (name, target_url, category) VALUES (?, ?, ?)",
            (name, target_url, category),
        )
        conn.commit()


def get_favorites() -> List[Dict[str, Any]]:
    """Obtiene la lista de favoritos."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM favorites ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]


def delete_favorite(fav_id: int) -> None:
    """Elimina un favorito por ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM favorites WHERE id = ?", (fav_id,))
        conn.commit()


def save_evidence(
    project_name: str,
    author_name: str,
    target_url: str,
    engine_name: str,
    device_name: str,
    findings: str,
    screenshot_path: str = "",
) -> None:
    """Guarda un registro de evidencia adaptándose a la estructura del esquema."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(evidences)")
        cols = [col["name"] for col in cursor.fetchall()]

        author_col = "author" if "author" in cols else "author_name"
        has_snap_col = "screenshot_path" in cols

        if has_snap_col:
            query = f"""INSERT INTO evidences 
                       (timestamp, project_name, {author_col}, target_url, engine_name, device_name, findings, screenshot_path) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
            params = (timestamp, project_name, author_name, target_url, engine_name, device_name, findings, screenshot_path)
        else:
            query = f"""INSERT INTO evidences 
                       (timestamp, project_name, {author_col}, target_url, engine_name, device_name, findings) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)"""
            params = (timestamp, project_name, author_name, target_url, engine_name, device_name, findings)

        cursor.execute(query, params)
        conn.commit()


def get_evidences() -> List[Dict[str, Any]]:
    """Obtiene el registro completo de evidencias ordenado por ID descendente."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evidences ORDER BY id DESC")
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            r = dict(row)
            if "author" in r and "author_name" not in r:
                r["author_name"] = r["author"]
            results.append(r)
        return results


def clear_all_project_data_and_history() -> None:
    """Limpia por completo las evidencias, historial de navegación y secuencia de IDs en SQLite optimizando el archivo con VACUUM."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM evidences")
        cursor.execute("DELETE FROM test_history")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('evidences', 'test_history')")
        conn.commit()
        cursor.execute("VACUUM")


def save_custom_profile(name: str, width: int, height: int, user_agent: str = "") -> None:
    """Guarda un perfil personalizado de dispositivo."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO custom_profiles (name, width, height, user_agent) VALUES (?, ?, ?, ?)",
            (name, width, height, user_agent),
        )
        conn.commit()


def get_custom_profiles() -> List[Dict[str, Any]]:
    """Obtiene los perfiles personalizados."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM custom_profiles ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]


def delete_custom_profile(profile_id: int) -> None:
    """Elimina un perfil personalizado."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM custom_profiles WHERE id = ?", (profile_id,))
        conn.commit()