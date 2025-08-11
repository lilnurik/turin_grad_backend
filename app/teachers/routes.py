from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.database import db, User
from app.utils.decorators import (
    success_response, get_pagination_params, create_pagination_response
)

teachers_bp = Blueprint('teachers', __name__)

@teachers_bp.route('', methods=['GET'])
@jwt_required()
def get_teachers():
    """Get list of teachers"""
    page, limit = get_pagination_params()
    
    query = User.query.filter_by(role='teacher')
    
    # Apply filters
    search = request.args.get('search')
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            db.or_(
                User.first_name.ilike(search_filter),
                User.last_name.ilike(search_filter),
                User.email.ilike(search_filter)
            )
        )
    
    faculty = request.args.get('faculty')
    if faculty:
        query = query.filter(User.faculty == faculty)
    
    query = query.order_by(User.created_at.desc())
    
    return success_response(create_pagination_response(query, page, limit))