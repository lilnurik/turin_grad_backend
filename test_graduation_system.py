#!/usr/bin/env python3
"""
Test script for the graduation system functionality
This script demonstrates the new features added to the student graduation system.
"""

from datetime import datetime

def test_graduation_system():
    """Test the graduation system functionality"""
    print("=== Student Graduation System Test ===\n")
    
    # Mock data to demonstrate functionality
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Academic year calculation (June to June)
    academic_year = current_year
    if current_month < 6:
        academic_year -= 1
    
    print(f"Current Academic Year: 06.{academic_year}-06.{academic_year + 1}")
    print(f"Current Date: {datetime.now().strftime('%d.%m.%Y')}")
    
    # Mock student data
    students = [
        {
            'name': 'Aziz Rahmonov',
            'student_id': '20210001',
            'admission_year': 2021,
            'graduation_year': 2025,
            'degree_level': 'bachelor',
            'student_type': 'regular',
            'student_status': 'current',
            'faculty': 'Факультет информатики'
        },
        {
            'name': 'Nodira Abdullayeva',
            'student_id': 'M20230001',
            'admission_year': 2023,
            'graduation_year': 2025,
            'degree_level': 'master',
            'student_type': 'regular',
            'student_status': 'current',
            'faculty': 'Экономический факультет'
        },
        {
            'name': 'Rustam Aminov',
            'student_id': 'P20220001',
            'admission_year': 2022,
            'graduation_year': 2025,
            'degree_level': 'phd',
            'student_type': 'regular',
            'student_status': 'current',
            'faculty': 'Факультет информатики'
        },
        {
            'name': 'Gulnara Saidova',
            'student_id': 'P20230002',
            'admission_year': 2023,
            'graduation_year': 2026,
            'degree_level': 'phd',
            'student_type': 'free_applicant',
            'student_status': 'current',
            'faculty': 'Экономический факультет'
        },
        {
            'name': 'Sarvar Karimov',
            'student_id': '20190001',
            'admission_year': 2019,
            'graduation_year': 2023,
            'degree_level': 'bachelor',
            'student_type': 'regular',
            'student_status': 'graduate',
            'faculty': 'Факультет информатики'
        }
    ]
    
    def is_eligible_for_graduation(student):
        """Check if student is eligible for graduation"""
        if student['student_status'] == 'graduate':
            return False
        graduation_date = datetime(student['graduation_year'], 6, 1)
        return datetime.now() >= graduation_date
    
    def get_academic_period(student):
        """Get academic period string"""
        return f"06.{student['admission_year']}-06.{student['graduation_year']}"
    
    def validate_graduation_data(student):
        """Validate graduation data"""
        errors = []
        duration = student['graduation_year'] - student['admission_year']
        
        if student['degree_level'] == 'bachelor' and duration not in [4, 5]:
            errors.append("Bachelor degree duration should be 4-5 years")
        elif student['degree_level'] == 'master' and duration not in [2, 3]:
            errors.append("Master degree duration should be 2-3 years")
        elif student['degree_level'] == 'phd' and duration not in [3, 4, 5]:
            errors.append("PhD duration should be 3-5 years")
        
        if student['degree_level'] in ['bachelor', 'master'] and student['student_type'] != 'regular':
            errors.append("Bachelor and Master students must be regular type")
        
        return errors
    
    print("\n=== Student Status Analysis ===")
    
    current_students = []
    graduates = []
    eligible_for_graduation = []
    
    for student in students:
        print(f"\n{student['name']} ({student['student_id']})")
        print(f"  Degree: {student['degree_level'].title()} ({student['student_type']})")
        print(f"  Period: {get_academic_period(student)}")
        print(f"  Faculty: {student['faculty']}")
        print(f"  Status: {student['student_status'].title()}")
        
        # Validation
        validation_errors = validate_graduation_data(student)
        if validation_errors:
            print(f"  ⚠️  Validation Issues: {', '.join(validation_errors)}")
        
        # Graduation eligibility
        if student['student_status'] == 'current':
            current_students.append(student)
            if is_eligible_for_graduation(student):
                eligible_for_graduation.append(student)
                print(f"  ✅ Eligible for graduation")
            else:
                print(f"  ⏳ Not yet eligible for graduation")
        else:
            graduates.append(student)
            print(f"  🎓 Already graduated")
    
    print(f"\n=== Summary Statistics ===")
    print(f"Total Students: {len(students)}")
    print(f"Current Students: {len(current_students)}")
    print(f"Graduates: {len(graduates)}")
    print(f"Eligible for Graduation: {len(eligible_for_graduation)}")
    
    # By degree level
    degree_stats = {}
    for degree in ['bachelor', 'master', 'phd', 'dsc']:
        current_count = len([s for s in current_students if s['degree_level'] == degree])
        graduate_count = len([s for s in graduates if s['degree_level'] == degree])
        degree_stats[degree] = {'current': current_count, 'graduates': graduate_count}
    
    print(f"\n=== By Degree Level ===")
    for degree, stats in degree_stats.items():
        if stats['current'] > 0 or stats['graduates'] > 0:
            print(f"{degree.title()}: {stats['current']} current, {stats['graduates']} graduates")
    
    # Students ready for graduation this year
    if eligible_for_graduation:
        print(f"\n=== Students Ready for Graduation ===")
        for student in eligible_for_graduation:
            print(f"  • {student['name']} ({student['degree_level'].title()})")
    
    print(f"\n=== API Endpoints Available ===")
    print("Admin Endpoints:")
    print("  GET /api/admin/graduating-students - List students eligible for graduation")
    print("  POST /api/admin/students/{id}/confirm-graduation - Confirm graduation")
    print("  POST /api/admin/students/{id}/revert-graduation - Revert graduation")
    print("  PUT /api/admin/students/{id}/graduation-info - Update graduation info")
    print("  GET /api/admin/graduation-statistics - Get graduation statistics")
    
    print("\nStudent Endpoints:")
    print("  GET /api/students?studentStatus=current - Filter current students")
    print("  GET /api/students?studentStatus=graduate - Filter graduates")
    print("  GET /api/students?degreeLevel=bachelor - Filter by degree level")
    print("  GET /api/students?degreeLevel=phd - Filter PhD students")
    
    print(f"\n=== Academic Year System ===")
    print("• Academic years run from June to June (e.g., 06.2024-06.2027)")
    print("• Students become eligible for graduation starting June of their graduation year")
    print("• Admins can confirm graduation status through the API")
    print("• All graduation actions are logged and generate notifications")
    
if __name__ == '__main__':
    test_graduation_system()