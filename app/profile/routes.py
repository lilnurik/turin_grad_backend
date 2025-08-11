from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db, User, WorkExperience, EducationGoal
from app.utils.decorators import (
    success_response, error_response, validate_json_data
)

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return error_response('USER_NOT_FOUND', 'User not found', status_code=404)
    
    return success_response(user.to_dict())

@profile_bp.route('', methods=['PUT'])
@jwt_required()
@validate_json_data()
def update_profile(data):
    """Update current user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return error_response('USER_NOT_FOUND', 'User not found', status_code=404)
    
    # Update allowed fields
    updatable_fields = [
        'firstName', 'lastName', 'middleName', 'phone', 'faculty', 'direction'
    ]
    
    field_map = {
        'firstName': 'first_name',
        'lastName': 'last_name',
        'middleName': 'middle_name'
    }
    
    for field in updatable_fields:
        if field in data:
            db_field = field_map.get(field, field)
            if hasattr(user, db_field):
                setattr(user, db_field, data[field])
    
    db.session.commit()
    
    return success_response(user.to_dict())

@profile_bp.route('/work-experience', methods=['GET'])
@jwt_required()
def get_work_experience():
    """Get user work experience"""
    current_user_id = get_jwt_identity()
    experiences = WorkExperience.query.filter_by(user_id=current_user_id).all()
    
    return success_response([exp.to_dict() for exp in experiences])

@profile_bp.route('/work-experience', methods=['POST'])
@jwt_required()
@validate_json_data(required_fields=['company', 'position', 'startDate'])
def add_work_experience(data):
    """Add work experience"""
    current_user_id = get_jwt_identity()
    
    from datetime import datetime
    
    try:
        start_date = datetime.fromisoformat(data['startDate']).date()
        end_date = None
        if 'endDate' in data and data['endDate']:
            end_date = datetime.fromisoformat(data['endDate']).date()
    except ValueError:
        return error_response('INVALID_DATE', 'Invalid date format', status_code=400)
    
    experience = WorkExperience(
        user_id=current_user_id,
        company=data['company'],
        position=data['position'],
        start_date=start_date,
        end_date=end_date,
        description=data.get('description')
    )
    
    db.session.add(experience)
    db.session.commit()
    
    return success_response(experience.to_dict(), status_code=201)

@profile_bp.route('/education-goals', methods=['GET'])
@jwt_required()
def get_education_goals():
    """Get user education goals"""
    current_user_id = get_jwt_identity()
    goals = EducationGoal.query.filter_by(user_id=current_user_id).all()
    
    return success_response([goal.to_dict() for goal in goals])

@profile_bp.route('/education-goals', methods=['POST'])
@jwt_required()
@validate_json_data(required_fields=['year', 'goal'])
def add_education_goal(data):
    """Add education goal"""
    current_user_id = get_jwt_identity()
    
    goal = EducationGoal(
        user_id=current_user_id,
        year=data['year'],
        goal=data['goal']
    )
    
    db.session.add(goal)
    db.session.commit()
    
    return success_response(goal.to_dict(), status_code=201)