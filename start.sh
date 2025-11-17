#!/bin/bash
#!/bin/bash
#!/bin/bash
gunicorn app:app -k eventlet --worker-connections 1000 --timeout 0 --bind 0.0.0.0:$PORT
