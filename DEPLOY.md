# 🚀 Деплой ДелоЗнаний на Railway (бесплатно)

## Структура проекта

```
├── server.py        — Flask-сервер (API + раздаёт index.html)
├── database.py      — работа с SQLite
├── index.html       — сайт
├── requirements.txt — зависимости Python
├── Procfile         — команда запуска для Railway
├── runtime.txt      — версия Python
└── .gitignore       — игнорируем .db файл
```

---

## Шаг 1 — Установи Git

Скачай с https://git-scm.com и установи.

Проверь в терминале:
```bash
git --version
```

---

## Шаг 2 — Создай репозиторий на GitHub

1. Зайди на https://github.com → нажми **New repository**
2. Название: `deloknany` (или любое)
3. Видимость: **Public**
4. Нажми **Create repository**

---

## Шаг 3 — Загрузи файлы на GitHub

В терминале, в папке с файлами проекта:

```bash
git init
git add .
git commit -m "Первый коммит"
git branch -M main
git remote add origin https://github.com/ТВО_ИМЯ/deloknany.git
git push -u origin main
```

> Замени `ТВО_ИМЯ` на свой логин GitHub.

---

## Шаг 4 — Задеплой на Railway

1. Зайди на https://railway.app
2. Нажми **Start a New Project**
3. Выбери **Deploy from GitHub repo**
4. Авторизуй GitHub и выбери репозиторий `deloknany`
5. Railway сам определит Python и запустит сервер

Через 1-2 минуты сайт будет доступен по адресу вида:
```
https://deloknany-production.up.railway.app
```

---

## Альтернатива — Render (тоже бесплатно)

1. Зайди на https://render.com
2. **New → Web Service**
3. Подключи GitHub репозиторий
4. Настройки:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python server.py`
5. Нажми **Create Web Service**

---

## ⚠️ Важно про базу данных на облаке

SQLite сохраняет данные в файл `deloknany.db` прямо на сервере Railway/Render. Это работает, но есть нюанс: **при каждом новом деплое файл базы сбрасывается** (все пользователи удаляются).

Для учебного проекта это нормально. Если захочешь постоянное хранение — напиши, добавлю PostgreSQL.

---

## Локальный запуск (для разработки)

```bash
pip install flask
python server.py
# открой http://localhost:8000
```
