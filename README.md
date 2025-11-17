# Selenium Test Runner

A Flask-based web application for automated URL testing using Selenium WebDriver.

## Features
- Web-based terminal interface
- Real-time test results
- User authentication
- Automated Chrome WebDriver testing

## Deployment to Railway

1. Push your code to GitHub
2. Connect your GitHub repository to Railway
3. Railway will automatically detect and deploy your Flask app

## Environment Variables
- `PORT`: Automatically set by Railway
- `RAILWAY_ENVIRONMENT`: Set to "production" by Railway

## Local Development
```bash
pip install -r requirements.txt
python app.py
```

Default login: admin/admin