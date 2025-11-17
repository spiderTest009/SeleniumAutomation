#!/bin/bash
#!/bin/bash
#!/bin/bash
gunicorn --worker-class=sync --workers=1 --bind=0.0.0.0:$PORT app:app
