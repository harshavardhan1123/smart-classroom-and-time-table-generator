import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, db

from models import Faculty

with app.app_context():
    f = Faculty.query.filter_by(email='yasir.afaq@srmap.edu.in').first()
    if f:
        print(f"Name: {f.name}")
        print(f"Email: {f.email}")
        if f.check_password("Yasir#SRM2026"):
            print("Password matches: Yasir#SRM2026")
        elif f.check_password("password123"):
            print("Password matches: password123")
        else:
            print("Password does not match known patterns.")
    else:
        print("Faculty not found.")
