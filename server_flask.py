"""
server.py — Flask-сервер для Railway/Render.
Раздаёт index.html и обрабатывает API запросы.
"""

import os
import json
from flask import Flask, request, jsonify, send_from_directory
import database as db

app = Flask(__name__, static_folder=".")

# ─── CORS (разрешаем запросы с любого домена) ───────────────────────────────
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@app.route("/api/<path:path>", methods=["OPTIONS"])
def options_handler(path):
    return "", 204

# ─── ФРОНТЕНД ───────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# ─── УТИЛИТЫ ────────────────────────────────────────────────────────────────
def get_token():
    auth = request.headers.get("Authorization", "")
    return auth[7:].strip() if auth.startswith("Bearer ") else ""

def err(msg, code=400):
    return jsonify({"error": msg}), code

# ─── POST /api/register ─────────────────────────────────────────────────────
@app.route("/api/register", methods=["POST"])
def register():
    body = request.get_json(silent=True) or {}
    name     = str(body.get("name", "")).strip()
    email    = str(body.get("email", "")).strip().lower()
    password = str(body.get("password", ""))

    if len(name) < 2:        return err("Имя слишком короткое — минимум 2 символа.")
    if "@" not in email:     return err("Некорректный формат e-mail.")
    if len(password) < 4:    return err("Пароль должен быть не короче 4 символов.")

    user = db.create_user(name, email, password)
    if user is None:
        return err("Этот e-mail уже зарегистрирован.", 409)

    token = db.create_session(user["id"])
    return jsonify({"message": "Регистрация прошла успешно!", "token": token, "user": user}), 201

# ─── POST /api/login ────────────────────────────────────────────────────────
@app.route("/api/login", methods=["POST"])
def login():
    body = request.get_json(silent=True) or {}
    email    = str(body.get("email", "")).strip().lower()
    password = str(body.get("password", ""))

    if not email or not password:
        return err("Введите e-mail и пароль.")

    row = db.get_user_by_email(email)
    if not row or not db.verify_password(password, row["password"]):
        return err("Неверный e-mail или пароль.", 401)

    token = db.create_session(row["id"])
    return jsonify({
        "message": "Вход выполнен.",
        "token": token,
        "user": {"id": row["id"], "name": row["name"], "email": row["email"]}
    })

# ─── POST /api/logout ───────────────────────────────────────────────────────
@app.route("/api/logout", methods=["POST"])
def logout():
    token = get_token()
    if token:
        db.delete_session(token)
    return jsonify({"message": "Вы вышли из аккаунта."})

# ─── GET /api/me ────────────────────────────────────────────────────────────
@app.route("/api/me")
def me():
    user = db.get_user_by_token(get_token())
    if not user:
        return err("Не авторизован.", 401)
    return jsonify({"id": user["id"], "name": user["name"],
                    "email": user["email"], "created_at": user["created_at"]})

# ─── GET /api/users ─────────────────────────────────────────────────────────
@app.route("/api/users")
def users():
    return jsonify({"users": db.get_all_users()})

# ─── GET /api/stats ─────────────────────────────────────────────────────────
@app.route("/api/stats")
def stats():
    return jsonify(db.db_stats())

# ─── ЗАПУСК ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    db.init_db()
    port = int(os.environ.get("PORT", 8000))
    print(f"Сервер запущен на порту {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
