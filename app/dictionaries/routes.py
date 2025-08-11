from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.database import db, Faculty, Direction, Company
from app.utils.decorators import (
    success_response, error_response, validate_json_data,
    get_pagination_params, create_pagination_response
)

dictionaries_bp = Blueprint('dictionaries', __name__)

@dictionaries_bp.route('/faculties', methods=['GET'])
@jwt_required()
def get_faculties():
    """Get list of faculties"""
    faculties = Faculty.query.order_by(Faculty.name).all()
    return success_response([faculty.to_dict() for faculty in faculties])

@dictionaries_bp.route('/directions', methods=['GET'])
@jwt_required()
def get_directions():
    """Get list of directions"""
    query = Direction.query
    
    # Filter by faculty if provided
    faculty_id = request.args.get('facultyId')
    if faculty_id:
        query = query.filter_by(faculty_id=faculty_id)
    
    directions = query.order_by(Direction.name).all()
    return success_response([direction.to_dict() for direction in directions])

@dictionaries_bp.route('/companies', methods=['GET'])
@jwt_required()
def get_companies():
    """Get list of companies"""
    page, limit = get_pagination_params()
    
    query = Company.query
    
    # Apply search filter
    search = request.args.get('search')
    if search:
        search_filter = f"%{search}%"
        query = query.filter(Company.name.ilike(search_filter))
    
    # Sort by name
    query = query.order_by(Company.name)
    
    return success_response(create_pagination_response(query, page, limit))

@dictionaries_bp.route('/companies', methods=['POST'])
@jwt_required()
@validate_json_data(required_fields=['name'])
def add_company(data):
    """Add a new company"""
    # Check if company already exists
    existing_company = Company.query.filter_by(name=data['name']).first()
    if existing_company:
        return error_response('COMPANY_EXISTS', 'Company already exists', status_code=400)
    
    company = Company(
        name=data['name'],
        website=data.get('website'),
        industry=data.get('industry'),
        location=data.get('location')
    )
    
    db.session.add(company)
    db.session.commit()
    
    return success_response(company.to_dict(), status_code=201)