from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.database import db, User, TeacherStudent
from app.utils.decorators import (
    role_required, success_response, error_response,
    get_pagination_params, create_pagination_response
)

students_bp = Blueprint('students', __name__)

@students_bp.route('', methods=['GET'])
@jwt_required()
def get_students(current_user=None):
    """Get list of students"""
    # This will be properly implemented with role checks
    page, limit = get_pagination_params()
    
    query = User.query.filter_by(role='student')
    
    # Apply filters
    search = request.args.get('search')
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            db.or_(
                User.first_name.ilike(search_filter),
                User.last_name.ilike(search_filter),
                User.email.ilike(search_filter),
                User.student_id.ilike(search_filter)
            )
        )
    
    faculty = request.args.get('faculty')
    if faculty:
        query = query.filter(User.faculty == faculty)
    
    query = query.order_by(User.created_at.desc())
    
    return success_response(create_pagination_response(query, page, limit))