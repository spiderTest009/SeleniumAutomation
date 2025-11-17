from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
import threading
import sqlite3
import hashlib
from functools import wraps
from datetime import datetime
from urltest import run_selenium_tests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'selenium-test-secret-key-super-secure'

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Global flags
test_running = False
stop_requested = False


def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        hashed = hashlib.sha256('admin'.encode()).hexdigest()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                       ('admin', hashed))
    conn.commit()
    conn.close()


init_db()


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrap


def emit_log(msg, level="info"):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    socketio.emit("log", {
        "timestamp": timestamp,
        "level": level,
        "message": msg
    })


def test_thread():
    global test_running, stop_requested
    try:
        run_selenium_tests(socketio, emit_log)
    finally:
        test_running = False
        stop_requested = False


@app.route('/')
def index():
    return redirect(url_for('dashboard') if 'logged_in' in session else 'login')


@app.route('/health')
def health():
    return "OK"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))

    error = None
    if request.method == 'POST':
        user = request.form.get("username")
        pwd = hashlib.sha256(request.form.get("password").encode()).hexdigest()

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (user, pwd))
        found = cursor.fetchone()
        conn.close()

        if found:
            session['logged_in'] = True
            session['username'] = user
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid username or password"

    return render_template('login.html', error=error)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session.get('username'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@socketio.on('start_test')
def start_test():
    global test_running, stop_requested

    if test_running:
        emit("error", {"message": "Tests are already running."})
        return

    # Simple test without Selenium first
    emit_log("Test started - checking connection...", "info")
    emit_log("SocketIO connection working!", "success")
    
    test_running = True
    stop_requested = False

    t = threading.Thread(target=test_thread)
    t.daemon = True
    t.start()


@socketio.on('stop_test')
def stop_test():
    global stop_requested
    stop_requested = True
    emit_log("Stop request received. Test will stop after current URL.", "warning")


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 5000))
    print(f"Starting SocketIO server on port {port}")
    socketio.run(app, host="0.0.0.0", port=port, debug=False, allow_unsafe_werkzeug=True)
