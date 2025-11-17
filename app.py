from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>🚀 Selenium Test Runner</h1><p>Server is running on Railway!</p><p><a href='/health'>Health Check</a></p>"

@app.route('/health')
def health():
    return "OK"

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port)
