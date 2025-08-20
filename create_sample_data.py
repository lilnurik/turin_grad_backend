#!/usr/bin/env python3
"""
Script to populate sample data for the Turin Grad Hub system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from app.database import db, User, Faculty, Direction, Company
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_sample_data():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///turin_grad.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Create faculties
        faculties_data = [
            {'name': 'Факультет информатики', 'description': 'Факультет информационных технологий и программирования'},
            {'name': 'Инженерный факультет', 'description': 'Инженерные специальности и технические науки'},
            {'name': 'Экономический факультет', 'description': 'Экономика, менеджмент и бизнес'},
            {'name': 'Факультет энергетики', 'description': 'Энергетические системы и технологии'}
        ]
        
        for faculty_data in faculties_data:
            existing = Faculty.query.filter_by(name=faculty_data['name']).first()
            if not existing:
                faculty = Faculty(**faculty_data)
                db.session.add(faculty)
        
        db.session.commit()
        
        # Create directions
        directions_data = [
            # IT Faculty
            {'faculty_name': 'Факультет информатики', 'name': 'Программная инженерия', 'description': 'Разработка программного обеспечения'},
            {'faculty_name': 'Факультет информатики', 'name': 'Информационные системы', 'description': 'Проектирование и администрирование ИС'},
            {'faculty_name': 'Факультет информатики', 'name': 'Кибербезопасность', 'description': 'Защита информации и систем'},
            
            # Engineering Faculty
            {'faculty_name': 'Инженерный факультет', 'name': 'Машиностроение', 'description': 'Конструирование и производство машин'},
            {'faculty_name': 'Инженерный факультет', 'name': 'Автоматизация', 'description': 'Автоматизация технологических процессов'},
            
            # Economics Faculty
            {'faculty_name': 'Экономический факультет', 'name': 'Экономика предприятия', 'description': 'Управление экономикой предприятий'},
            {'faculty_name': 'Экономический факультет', 'name': 'Международная экономика', 'description': 'Международные экономические отношения'},
            
            # Energy Faculty
            {'faculty_name': 'Факультет энергетики', 'name': 'Электроэнергетика', 'description': 'Электрические станции и сети'},
            {'faculty_name': 'Факультет энергетики', 'name': 'Возобновляемая энергетика', 'description': 'Альтернативные источники энергии'}
        ]
        
        for direction_data in directions_data:
            faculty = Faculty.query.filter_by(name=direction_data['faculty_name']).first()
            if faculty:
                existing = Direction.query.filter_by(name=direction_data['name'], faculty_id=faculty.id).first()
                if not existing:
                    direction = Direction(
                        faculty_id=faculty.id,
                        name=direction_data['name'],
                        description=direction_data['description']
                    )
                    db.session.add(direction)
        
        db.session.commit()
        
        # Create companies
        companies_data = [
            {'name': 'EPAM Systems', 'website': 'https://epam.com', 'industry': 'IT', 'location': 'Ташкент'},
            {'name': 'UZINFOCOM', 'website': 'https://uzinfocom.uz', 'industry': 'IT', 'location': 'Ташкент'},
            {'name': 'UzbekTelecom', 'website': 'https://uztelecom.uz', 'industry': 'Телекоммуникации', 'location': 'Ташкент'},
            {'name': 'Artel', 'website': 'https://artelelectronics.com', 'industry': 'Электроника', 'location': 'Ташкент'},
            {'name': 'Uzautomotors', 'website': 'https://uzautomotors.com', 'industry': 'Автомобилестроение', 'location': 'Андижан'},
            {'name': 'Narx.uz', 'website': 'https://narx.uz', 'industry': 'E-commerce', 'location': 'Ташкент'},
            {'name': 'ITIC', 'website': 'https://itic.uz', 'industry': 'IT', 'location': 'Ташкент'},
            {'name': 'Kapitalbank', 'website': 'https://kapitalbank.uz', 'industry': 'Банковское дело', 'location': 'Ташкент'},
            {'name': 'UzbekEnergo', 'website': 'https://uzbekenergo.uz', 'industry': 'Энергетика', 'location': 'Ташкент'},
            {'name': 'AGMK', 'website': 'https://agmk.uz', 'industry': 'Горнодобыча', 'location': 'Алмалык'}
        ]
        
        for company_data in companies_data:
            existing = Company.query.filter_by(name=company_data['name']).first()
            if not existing:
                company = Company(**company_data)
                db.session.add(company)
        
        db.session.commit()
        
        # Create sample students and teachers
        sample_users = [
            # Teachers
            {
                'first_name': 'Dilshod',
                'last_name': 'Karimov',
                'email': 'd.karimov@ttpu.uz',
                'role': 'teacher',
                'faculty': 'Факультет информатики',
                'is_verified': True,
                'email_verified': True
            },
            {
                'first_name': 'Sevara',
                'last_name': 'Nazarova',
                'email': 's.nazarova@ttpu.uz',
                'role': 'teacher',
                'faculty': 'Экономический факультет',
                'is_verified': True,
                'email_verified': True
            },
            
            # Students
            {
                'first_name': 'Aziz',
                'last_name': 'Rahmonov',
                'email': 'a.rahmonov@student.ttpu.uz',
                'student_id': '20210001',
                'role': 'student',
                'faculty': 'Факультет информатики',
                'direction': 'Программная инженерия',
                'admission_year': 2021,
                'graduation_year': 2025,
                'financing_type': 'budget',
                'student_status': 'current',
                'degree_level': 'bachelor',
                'student_type': 'regular',
                'phone': '+998901234501',
                'is_verified': True,
                'email_verified': True
            },
            {
                'first_name': 'Madina',
                'last_name': 'Usmanova',
                'email': 'm.usmanova@student.ttpu.uz',
                'student_id': '20210002',
                'role': 'student',
                'faculty': 'Экономический факультет',
                'direction': 'Экономика предприятия',
                'admission_year': 2021,
                'graduation_year': 2025,
                'financing_type': 'contract',
                'student_status': 'current',
                'degree_level': 'bachelor',
                'student_type': 'regular',
                'phone': '+998901234502',
                'is_verified': True,
                'email_verified': True
            },
            {
                'first_name': 'Bobur',
                'last_name': 'Tursunov',
                'email': 'b.tursunov@student.ttpu.uz',
                'student_id': '20220001',
                'role': 'student',
                'faculty': 'Инженерный факультет',
                'direction': 'Автоматизация',
                'admission_year': 2022,
                'graduation_year': 2026,
                'financing_type': 'budget',
                'student_status': 'current',
                'degree_level': 'bachelor',
                'student_type': 'regular',
                'phone': '+998901234503',
                'is_verified': False,  # Pending verification
                'email_verified': True
            },
            # Graduate students with different degree levels
            {
                'first_name': 'Sarvar',
                'last_name': 'Karimov',
                'email': 's.karimov@student.ttpu.uz',
                'student_id': '20190001',
                'role': 'student',
                'faculty': 'Факультет информатики',
                'direction': 'Компьютерные системы',
                'admission_year': 2019,
                'graduation_year': 2023,
                'financing_type': 'budget',
                'student_status': 'graduate',
                'degree_level': 'bachelor',
                'student_type': 'regular',
                'phone': '+998901234504',
                'is_verified': True,
                'email_verified': True
            },
            # Master's student
            {
                'first_name': 'Nodira',
                'last_name': 'Abdullayeva',
                'email': 'n.abdullayeva@student.ttpu.uz',
                'student_id': 'M20230001',
                'role': 'student',
                'faculty': 'Экономический факультет',
                'direction': 'Финансы и кредит',
                'admission_year': 2023,
                'graduation_year': 2025,
                'financing_type': 'contract',
                'student_status': 'current',
                'degree_level': 'master',
                'student_type': 'regular',
                'phone': '+998901234505',
                'is_verified': True,
                'email_verified': True
            },
            # PhD student
            {
                'first_name': 'Rustam',
                'last_name': 'Aminov',
                'email': 'r.aminov@student.ttpu.uz',
                'student_id': 'P20220001',
                'role': 'student',
                'faculty': 'Факультет информатики',
                'direction': 'Информационные технологии',
                'admission_year': 2022,
                'graduation_year': 2025,
                'financing_type': 'budget',
                'student_status': 'current',
                'degree_level': 'phd',
                'student_type': 'regular',
                'phone': '+998901234506',
                'is_verified': True,
                'email_verified': True
            },
            # PhD free applicant
            {
                'first_name': 'Gulnara',
                'last_name': 'Saidova',
                'email': 'g.saidova@student.ttpu.uz',
                'student_id': 'P20230002',
                'role': 'student',
                'faculty': 'Экономический факультет',
                'direction': 'Экономическая теория',
                'admission_year': 2023,
                'graduation_year': 2026,
                'financing_type': 'contract',
                'student_status': 'current',
                'degree_level': 'phd',
                'student_type': 'free_applicant',
                'phone': '+998901234507',
                'is_verified': True,
                'email_verified': True
            }
        ]
        
        for user_data in sample_users:
            existing = User.query.filter_by(email=user_data['email']).first()
            if not existing:
                user = User(**user_data)
                user.set_password('password123')  # Default password
                db.session.add(user)
        
        db.session.commit()
        
        print("Sample data created successfully!")
        print(f"- {len(faculties_data)} faculties")
        print(f"- {len(directions_data)} directions")
        print(f"- {len(companies_data)} companies")
        print(f"- {len(sample_users)} users (teachers and students)")

if __name__ == "__main__":
    create_sample_data()