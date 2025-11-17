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
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
test_running = False
stop_requested = False



# Database initialization
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
    
    # Check if admin user exists
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        # Hash the password
        hashed_password = hashlib.sha256('admin'.encode()).hexdigest()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                      ('admin', hashed_password))
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def emit_log(message, level="info"):
    """Emit log message to frontend"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    socketio.emit('log', {
        'timestamp': timestamp,
        'level': level,
        'message': message
    })

def run_tests_wrapper():
    """Wrapper function to run tests with global state management"""
    global test_running, stop_requested
    
    try:
        run_selenium_tests(socketio, emit_log)
    finally:
        test_running = False
        stop_requested = False

@app.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Hash the input password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Check credentials
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                      (username, hashed_password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid credentials'
    
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
def handle_start_test():
    global test_running, stop_requested
    
    if 'logged_in' not in session:
        return
    
    if test_running:
        emit('error', {'message': 'Tests are already running'})
        return
    
    test_running = True
    stop_requested = False
    
    thread = threading.Thread(target=run_tests_wrapper)
    thread.daemon = True
    thread.start()

@socketio.on('stop_test')
def handle_stop_test():
    global stop_requested
    
    if 'logged_in' not in session:
        return
    
    stop_requested = True
    emit_log("Stop requested, waiting for current test to finish...", "warning")

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, debug=False, host='0.0.0.0', port=port)