# Project Dependencies

This document lists all the dependencies required for the Neural Text-to-Speech with Sound Playground application.

## Python Packages
- **flask**: Web framework for the application
- **flask-sqlalchemy**: SQL toolkit for Flask
- **gtts**: Google Text-to-Speech library
- **gunicorn**: WSGI HTTP Server for production
- **psycopg2-binary**: PostgreSQL adapter for Python
- **pydub**: Audio processing library
- **email-validator**: For validating email addresses
- **routes**: Route declaration system for Python

## JavaScript Libraries
- **Bootstrap 5**: CSS framework with Replit dark theme
- **Bootstrap Icons**: Icon set for UI elements

## Installation

All the necessary Python dependencies are already installed in the Replit environment. If you're deploying this project outside of Replit, you can install the dependencies using pip:

```
pip install flask flask-sqlalchemy gtts gunicorn psycopg2-binary pydub email-validator routes
```

For the frontend, the application uses CDN-hosted libraries:
- Bootstrap: `https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css`
- Bootstrap Icons: `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css`