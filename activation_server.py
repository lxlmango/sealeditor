from __future__ import annotations

import os
import secrets
import sqlite3
import string
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from flask import Flask, jsonify, redirect, render_template_string, request, session, url_for
from flask_cors import CORS

DEFAULT_CODE_LENGTH = 12
DEFAULT_VALID_HOURS = 24
DB_PATH = os.path.join(os.path.dirname(__file__), "activation_store.db")
CLEANUP_DEFAULT_TIME = os.environ.get("CLEANUP_TIME", "03:00")

ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "Test*963.")
SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(16))

app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    conn = _db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS codes (
            code TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            last_verified_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    cur.execute(
        "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
        ("cleanup_enabled", "1"),
    )
    cur.execute(
        "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
        ("cleanup_time", CLEANUP_DEFAULT_TIME),
    )
    cur.execute(
        "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
        ("last_cleanup_date", ""),
    )
    conn.commit()
    conn.close()


def _cleanup_expired() -> None:
    now_iso = _iso(_utc_now())
    conn = _db()
    cur = conn.cursor()
    cur.execute("DELETE FROM codes WHERE expires_at < ?", (now_iso,))
    conn.commit()
    conn.close()


def _get_setting(key: str, default: str = "") -> str:
    conn = _db()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return default
    return row["value"]


def _set_setting(key: str, value: str) -> None:
    conn = _db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
    conn.commit()
    conn.close()


def _start_cleanup_job() -> None:
    def _loop() -> None:
        last_checked = ""
        while True:
            try:
                enabled = _get_setting("cleanup_enabled", "1") == "1"
                if enabled:
                    now_local = datetime.now()
                    today = now_local.strftime("%Y-%m-%d")
                    cleanup_time = _get_setting("cleanup_time", CLEANUP_DEFAULT_TIME)
                    last_run = _get_setting("last_cleanup_date", "")
                    current_hm = now_local.strftime("%H:%M")
                    if current_hm == cleanup_time and last_run != today and last_checked != today:
                        _cleanup_expired()
                        _set_setting("last_cleanup_date", today)
                        last_checked = today
            except Exception:
                pass
            time.sleep(30)

    thread = threading.Thread(target=_loop, daemon=True)
    thread.start()


def _generate_code(length: int = DEFAULT_CODE_LENGTH) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _require_admin() -> Optional[any]:
    if session.get("admin") is True:
        return None
    return redirect(url_for("admin_login"))


@app.post("/api/activation/verify")
def verify_code():
    payload = request.get_json(silent=True) or {}
    code = str(payload.get("code", "")).strip().upper()
    if not code:
        return jsonify({"valid": False, "reason": "missing_code"}), 400

    conn = _db()
    cur = conn.cursor()
    cur.execute("SELECT code, expires_at FROM codes WHERE code = ?", (code,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({"valid": False, "reason": "not_found"}), 404

    now = _utc_now()
    expires_at = datetime.fromisoformat(row["expires_at"])
    if now > expires_at:
        conn.close()
        return jsonify({"valid": False, "reason": "expired", "expiresAt": row["expires_at"]})

    cur.execute(
        "UPDATE codes SET last_verified_at = ? WHERE code = ?",
        (_iso(now), code),
    )
    conn.commit()
    conn.close()
    return jsonify({"valid": True, "expiresAt": row["expires_at"]})


@app.post("/api/activation/generate")
def generate_codes_api():
    # Optional: allow programmatic generation if admin session exists
    if session.get("admin") is not True:
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    return _generate_codes(payload)


def _generate_codes(payload: dict):
    count = int(payload.get("count", 1))
    hours_valid = int(payload.get("hours_valid", DEFAULT_VALID_HOURS))
    length = int(payload.get("length", DEFAULT_CODE_LENGTH))

    count = max(1, min(count, 1000))
    length = max(6, min(length, 32))
    hours_valid = max(1, min(hours_valid, 720))

    _cleanup_expired()

    created_at = _utc_now()
    expires_at = created_at + timedelta(hours=hours_valid)

    conn = _db()
    cur = conn.cursor()

    # load existing codes to avoid collisions
    cur.execute("SELECT code FROM codes")
    existing = {row["code"] for row in cur.fetchall()}

    codes = []
    while len(codes) < count:
        code = _generate_code(length)
        if code in existing:
            continue
        existing.add(code)
        cur.execute(
            "INSERT INTO codes (code, created_at, expires_at, last_verified_at) VALUES (?, ?, ?, ?)",
            (code, _iso(created_at), _iso(expires_at), None),
        )
        codes.append(code)

    conn.commit()
    conn.close()

    return jsonify({"count": len(codes), "codes": codes, "expires_at": _iso(expires_at)})


@app.get("/admin")
def admin_home():
    guard = _require_admin()
    if guard is not None:
        return guard

    _cleanup_expired()

    cleanup_enabled = _get_setting("cleanup_enabled", "1")
    cleanup_time = _get_setting("cleanup_time", CLEANUP_DEFAULT_TIME)
    last_cleanup_date = _get_setting("last_cleanup_date", "")

    conn = _db()
    cur = conn.cursor()
    cur.execute(
        "SELECT code, created_at, expires_at, last_verified_at FROM codes ORDER BY created_at DESC LIMIT 200"
    )
    rows = cur.fetchall()
    conn.close()

    return render_template_string(
        """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>激活码管理</title>
          <style>
            body { font-family: Arial, sans-serif; background:#0f1115; color:#eef0f4; margin:0; padding:20px; }
            .card { background:#171b22; padding:20px; border-radius:12px; margin-bottom:16px; }
            input, select, button { padding:8px 10px; border-radius:8px; border:1px solid #2a2f3a; background:#0f1115; color:#eef0f4; }
            button { cursor:pointer; background:#ff6a57; border:none; color:#fff; font-weight:600; }
            table { width:100%; border-collapse: collapse; font-size: 13px; }
            th, td { border-bottom:1px solid #2a2f3a; padding:8px; text-align:left; }
            .row { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
            .muted { color:#9aa3b2; font-size:12px; }
          </style>
        </head>
        <body>
          <div class="card">
            <h2>生成激活码</h2>
            <form method="post" action="/admin/generate">
              <div class="row">
                <label>数量</label>
                <input name="count" type="number" min="1" max="1000" value="10" />
                <label>有效期(小时)</label>
                <input name="hours_valid" type="number" min="1" max="720" value="24" />
                <label>码长度</label>
                <input name="length" type="number" min="6" max="32" value="12" />
                <button type="submit">生成</button>
                <a href="/admin/logout" style="color:#ffb14a;text-decoration:none;">退出</a>
              </div>
            </form>
            {% if generated %}
              <div class="muted" style="margin-top:10px;">刚生成：{{ generated|length }} 个</div>
              <pre>{{ generated|join("\n") }}</pre>
            {% endif %}
          </div>
          <div class="card">
            <h2>定时清理</h2>
            <form method="post" action="/admin/settings">
              <div class="row">
                <label>开启</label>
                <select name="cleanup_enabled">
                  <option value="1" {% if cleanup_enabled == '1' %}selected{% endif %}>是</option>
                  <option value="0" {% if cleanup_enabled != '1' %}selected{% endif %}>否</option>
                </select>
                <label>每天时间</label>
                <input name="cleanup_time" type="text" value="{{ cleanup_time }}" placeholder="HH:MM" />
                <button type="submit">保存</button>
              </div>
              <div class="muted" style="margin-top:8px;">上次清理：{{ last_cleanup_date or '暂无' }}</div>
            </form>
            <form method="post" action="/admin/cleanup" style="margin-top:12px;">
              <button type="submit">立即清理</button>
            </form>
          </div>
          <div class="card">
            <h2>最近激活码</h2>
            <table>
              <thead>
                <tr>
                  <th>激活码</th>
                  <th>创建时间</th>
                  <th>过期时间</th>
                  <th>最近验证</th>
                </tr>
              </thead>
              <tbody>
                {% for row in rows %}
                <tr>
                  <td>{{ row['code'] }}</td>
                  <td>{{ row['created_at'] }}</td>
                  <td>{{ row['expires_at'] }}</td>
                  <td>{{ row['last_verified_at'] or '-' }}</td>
                </tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
        </body>
        </html>
        """,
        rows=rows,
        generated=session.pop("generated", None),
        cleanup_enabled=cleanup_enabled,
        cleanup_time=cleanup_time,
        last_cleanup_date=last_cleanup_date,
    )


@app.get("/admin/login")
def admin_login():
    return render_template_string(
        """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>管理员登录</title>
          <style>
            body { font-family: Arial, sans-serif; background:#0f1115; color:#eef0f4; display:flex; align-items:center; justify-content:center; height:100vh; }
            .card { background:#171b22; padding:24px; border-radius:12px; width:320px; }
            input { width:100%; padding:10px; margin:8px 0; border-radius:8px; border:1px solid #2a2f3a; background:#0f1115; color:#eef0f4; }
            button { width:100%; padding:10px; border-radius:8px; border:none; background:#ff6a57; color:#fff; font-weight:600; cursor:pointer; }
          </style>
        </head>
        <body>
          <form class="card" method="post" action="/admin/login">
            <h2>管理员登录</h2>
            <input name="username" placeholder="用户名" />
            <input name="password" type="password" placeholder="密码" />
            <button type="submit">登录</button>
          </form>
        </body>
        </html>
        """
    )


@app.post("/admin/login")
def admin_login_post():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    if username == ADMIN_USER and password == ADMIN_PASS:
        session["admin"] = True
        return redirect(url_for("admin_home"))
    return redirect(url_for("admin_login"))


@app.get("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))


@app.post("/admin/generate")
def admin_generate():
    guard = _require_admin()
    if guard is not None:
        return guard

    payload = {
        "count": request.form.get("count", 10),
        "hours_valid": request.form.get("hours_valid", DEFAULT_VALID_HOURS),
        "length": request.form.get("length", DEFAULT_CODE_LENGTH),
    }
    response = _generate_codes(payload)
    data = response.get_json()
    session["generated"] = data.get("codes", [])
    return redirect(url_for("admin_home"))


@app.post("/admin/settings")
def admin_settings():
    guard = _require_admin()
    if guard is not None:
        return guard

    enabled = request.form.get("cleanup_enabled", "1")
    cleanup_time = request.form.get("cleanup_time", CLEANUP_DEFAULT_TIME).strip()
    if len(cleanup_time) != 5 or cleanup_time[2] != ":":
        cleanup_time = CLEANUP_DEFAULT_TIME

    _set_setting("cleanup_enabled", "1" if enabled == "1" else "0")
    _set_setting("cleanup_time", cleanup_time)
    return redirect(url_for("admin_home"))


@app.post("/admin/cleanup")
def admin_cleanup():
    guard = _require_admin()
    if guard is not None:
        return guard

    _cleanup_expired()
    _set_setting("last_cleanup_date", datetime.now().strftime("%Y-%m-%d"))
    return redirect(url_for("admin_home"))


if __name__ == "__main__":
    _init_db()
    _start_cleanup_job()
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True)
