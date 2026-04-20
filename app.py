"""
UniSchedule — University Timetable Management System
Main application entry point. Configures Flask, registers blueprints, and starts server.
"""
import os, sys

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from dotenv import load_dotenv

from models import db

# ─── Load environment ───────────────────────────────────────
load_dotenv()

# ─── Mandatory env var checks ───────────────────────────────
_secret_key = os.getenv('FLASK_SECRET_KEY')
if not _secret_key:
    sys.exit("FATAL: FLASK_SECRET_KEY is not set in .env. Refusing to start with an insecure key.")

_admin_password = os.getenv('ADMIN_PASSWORD')
if not _admin_password:
    sys.exit("FATAL: ADMIN_PASSWORD is not set in .env. Cannot start without admin credentials.")

# ─── Create app ─────────────────────────────────────────────
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///university.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = _secret_key

# ─── CSRF Protection ────────────────────────────────────────
csrf = CSRFProtect(app)

# ─── Database ───────────────────────────────────────────────
db.init_app(app)
migrate = Migrate(app, db)

# Fallback: create tables directly if no migrations folder exists (first run)
with app.app_context():
    if not os.path.isdir(os.path.join(os.path.dirname(__file__), 'migrations')):
        db.create_all()

# ─── Register Blueprints ────────────────────────────────────
from blueprints.auth import auth
from blueprints.admin import admin
from blueprints.faculty import faculty_bp
from blueprints.student import student_bp
from blueprints.api import api
from blueprints.chatbot_admin import chatbot_admin_bp
from blueprints.chatbot_faculty import chatbot_faculty_bp
from blueprints.chatbot_student import chatbot_student_bp

app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(faculty_bp)
app.register_blueprint(student_bp)
app.register_blueprint(api)  # url_prefix='/api' set in blueprint
app.register_blueprint(chatbot_admin_bp)
app.register_blueprint(chatbot_faculty_bp)
app.register_blueprint(chatbot_student_bp)

# Exempt JSON-only blueprints from CSRF (protected by session auth)
# Auth blueprint keeps CSRF for login form POST
csrf.exempt(api)
csrf.exempt(student_bp)
csrf.exempt(faculty_bp)
csrf.exempt(chatbot_admin_bp)
csrf.exempt(chatbot_faculty_bp)
csrf.exempt(chatbot_student_bp)

# ─── Run ─────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    app.run(debug=debug, port=port)
