from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.database import db, User, Company
from app.utils.decorators import (
    success_response, get_pagination_params, create_pagination_response
)

search_bp = Blueprint('search', __name__)

@search_bp.route('', methods=['GET'])
@jwt_required()
def global_search():
    """Global search across the system"""
    q = request.args.get('q', '').strip()
    if not q:
        return success_response({'users': [], 'companies': []})
    
    search_type = request.args.get('type', 'all')
    page, limit = get_pagination_params()
    
    results = {}
    search_filter = f"%{q}%"
    
    if search_type in ['all', 'users']:
        # Search users
        user_query = User.query.filter(
            db.or_(
                User.first_name.ilike(search_filter),
                User.last_name.ilike(search_filter),
                User.email.ilike(search_filter),
                User.student_id.ilike(search_filter)
            )
        ).order_by(User.created_at.desc())
        
        if search_type == 'users':
            results = create_pagination_response(user_query, page, limit)
        else:
            results['users'] = [user.to_dict() for user in user_query.limit(10).all()]
    
    if search_type in ['all', 'companies']:
        # Search companies
        company_query = Company.query.filter(
            Company.name.ilike(search_filter)
        ).order_by(Company.name)
        
        if search_type == 'companies':
            results = create_pagination_response(company_query, page, limit)
        else:
            results['companies'] = [company.to_dict() for company in company_query.limit(10).all()]
    
    return success_response(results)

@search_bp.route('/students', methods=['GET'])
@jwt_required()
def search_students():
    """Search students with advanced filters"""
    page, limit = get_pagination_params()
    
    # Base query for students
    query = User.query.filter_by(role='student')
    
    # Apply filters
    q = request.args.get('q')
    if q:
        search_filter = f"%{q}%"
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
    
    direction = request.args.get('direction')
    if direction:
        query = query.filter(User.direction == direction)
    
    admission_year = request.args.get('admissionYear', type=int)
    if admission_year:
        query = query.filter(User.admission_year == admission_year)
    
    graduation_year = request.args.get('graduationYear', type=int)
    if graduation_year:
        query = query.filter(User.graduation_year == graduation_year)
    
    # Sort by name
    query = query.order_by(User.first_name, User.last_name)
    
    return success_response(create_pagination_response(query, page, limit))