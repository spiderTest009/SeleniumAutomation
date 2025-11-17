#!/usr/bin/env python3

import os
from flask import Flask

# Create Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>🚀 Railway Flask Test</h1>
    <p>✅ Server is running successfully!</p>
    <p>Port: {}</p>
    <p><a href="/health">Health Check</a></p>
    '''.format(os.getenv('PORT', 'Unknown'))

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f'🚀 Starting server on port {port}')
    print(f'🌐 Environment PORT: {os.getenv("PORT", "Not set")}')
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )