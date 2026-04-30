import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, db
from models import Faculty, Student, Course

with app.app_context():
    # 1. Admin Info
    from blueprints.utils import ADMIN_EMAIL
    admin_pass = os.environ.get('ADMIN_PASSWORD', 'Not set in env')
    print(f"Admin Email: {ADMIN_EMAIL}")
    print(f"Admin Password: {admin_pass}")
    
    print("-" * 20)
    
    # 2. Student under Yasir
    yasir = Faculty.query.filter_by(faculty_uid='FAC001').first()
    if yasir:
        print(f"Faculty: {yasir.name} ({yasir.email})")
        # Get courses Yasir teaches
        course_ids = [c.id for c in yasir.courses_can_teach]
        
        # Find a student enrolled in one of these courses
        student = Student.query.join(Student.courses_enrolled).filter(Course.id.in_(course_ids)).first()
        
        if student:
            print(f"Student under Yasir: {student.name}")
            print(f"Email: {student.email}")
            
            # Check password patterns
            from models import generate_email_from_name
            # Based on reset_all_passwords_v2.py logic
            import re
            def get_first_name(name):
                cleaned = re.sub(r'^(Dr\.?|Prof\.?|Mr\.?|Mrs\.?|Ms\.?)\s+', '', name.strip(), flags=re.IGNORECASE)
                parts = cleaned.strip().split()
                return parts[0] if parts else 'User'
            
            fname = get_first_name(student.name)
            pattern_pass = f"{fname}#SRM2026"
            
            if student.check_password(pattern_pass):
                print(f"Password: {pattern_pass}")
            elif student.check_password("password123"):
                print("Password: password123")
            else:
                print("Password: Unknown (does not match common patterns)")
        else:
            print("No student found under Yasir.")
    else:
        print("Faculty Yasir (FAC001) not found.")
