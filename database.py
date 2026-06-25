"""
database.py — инициализация SQLite и все операции с БД
"""

import sqlite3
import hashlib
import secrets
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "deloknany.db")


# ─────────────────────────────────────────────
#  ПОДКЛЮЧЕНИЕ
# ─────────────────────────────────────────────

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # возвращает строки как dict
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ─────────────────────────────────────────────
#  СОЗДАНИЕ ТАБЛИЦ
# ─────────────────────────────────────────────

SCHEMA = """
-- Пользователи
CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    email      TEXT    NOT NULL UNIQUE,
    password   TEXT    NOT NULL,          -- SHA-256 хэш
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Сессионные токены (вместо JWT — простые random-токены)
CREATE TABLE IF NOT EXISTS sessions (
    token      TEXT    PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);
"""

def init_db():
    """Создаёт таблицы если их нет. Запускается при старте сервера."""
    with get_connection() as conn:
        conn.executescript(SCHEMA)
    print(f"[DB] База данных готова: {DB_PATH}")


# ─────────────────────────────────────────────
#  ХЭШИРОВАНИЕ ПАРОЛЯ
# ─────────────────────────────────────────────

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


# ─────────────────────────────────────────────
#  ПОЛЬЗОВАТЕЛИ
# ─────────────────────────────────────────────

def create_user(name: str, email: str, password: str) -> dict | None:
    """
    Создаёт пользователя. Возвращает dict пользователя или None если email занят.
    """
    try:
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name.strip(), email.lower().strip(), hash_password(password))
            )
            user_id = cur.lastrowid
            return {"id": user_id, "name": name.strip(), "email": email.lower().strip()}
    except sqlite3.IntegrityError:
        return None  # email уже занят


def get_user_by_email(email: str) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.lower().strip(),)
        ).fetchone()


def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, name, email, created_at FROM users WHERE id = ?", (user_id,)
        ).fetchone()


def get_all_users() -> list:
    """Возвращает всех пользователей (без паролей) — для отладки."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, email, created_at FROM users ORDER BY id"
        ).fetchall()
        return [dict(r) for r in rows]


# ─────────────────────────────────────────────
#  СЕССИИ / ТОКЕНЫ
# ─────────────────────────────────────────────

def create_session(user_id: int) -> str:
    """Создаёт токен сессии и сохраняет в БД. Возвращает токен."""
    token = secrets.token_hex(32)
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO sessions (token, user_id) VALUES (?, ?)",
            (token, user_id)
        )
    return token


def get_user_by_token(token: str) -> sqlite3.Row | None:
    """Проверяет токен и возвращает пользователя."""
    if not token:
        return None
    with get_connection() as conn:
        return conn.execute(
            """SELECT u.id, u.name, u.email, u.created_at
               FROM sessions s
               JOIN users u ON u.id = s.user_id
               WHERE s.token = ?""",
            (token,)
        ).fetchone()


def delete_session(token: str):
    """Удаляет токен (выход из аккаунта)."""
    with get_connection() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))


def delete_all_user_sessions(user_id: int):
    """Удаляет все сессии пользователя."""
    with get_connection() as conn:
        conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))


# ─────────────────────────────────────────────
#  УТИЛИТЫ
# ─────────────────────────────────────────────

def db_stats() -> dict:
    """Статистика БД для дебага."""
    with get_connection() as conn:
        users_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        sessions_count = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        return {
            "db_path": DB_PATH,
            "users": users_count,
            "active_sessions": sessions_count
        }
