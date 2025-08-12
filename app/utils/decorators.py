from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.database import User
import re
import phonenumbers
from email_validator import validate_email, EmailNotValidError

def role_required(*roles):
    """Decorator to check if user has required role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'USER_NOT_FOUND',
                        'message': 'User not found'
                    }
                }), 404
            
            if user.is_blocked:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'USER_BLOCKED',
                        'message': 'User account is blocked'
                    }
                }), 403
            
            if user.role not in roles:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INSUFFICIENT_PERMISSIONS',
                        'message': 'Insufficient permissions'
                    }
                }), 403
            
            return f(current_user=user, *args, **kwargs)
        return decorated_function
    return decorator

def verified_required(f):
    """Decorator to check if user is verified"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': 'User not found'
                }
            }), 404
        
        if not user.is_verified:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'USER_NOT_VERIFIED',
                    'message': 'User account is not verified'
                }
            }), 403
        
        return f(current_user=user, *args, **kwargs)
    return decorated_function

def validate_email_format(email):
    """Validate email format using simple regex"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone_format(phone):
    """Validate phone number format"""
    try:
        parsed = phonenumbers.parse(phone, "UZ")
        return phonenumbers.is_valid_number(parsed)
    except:
        return False

def validate_student_id(student_id):
    """Validate student ID format (8 digits)"""
    return bool(re.match(r'^\d{8}$', student_id))

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, ""

def get_pagination_params():
    """Get pagination parameters from request"""
    page = request.args.get('page', 1, type=int)
    limit = min(request.args.get('limit', 20, type=int), 100)  # Max 100 items per page
    return page, limit

def create_pagination_response(query, page, limit):
    """Create paginated response"""
    paginated = query.paginate(
        page=page, 
        per_page=limit, 
        error_out=False
    )
    
    return {
        'data': [item.to_dict() for item in paginated.items],
        'pagination': {
            'page': page,
            'limit': limit,
            'total': paginated.total,
            'totalPages': paginated.pages
        }
    }

def validate_json_data(required_fields=None, optional_fields=None):
    """Decorator to validate JSON data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_CONTENT_TYPE',
                        'message': 'Content-Type must be application/json'
                    }
                }), 400
            
            data = request.get_json()
            errors = []
            
            # Check required fields
            if required_fields:
                for field in required_fields:
                    if field not in data or data[field] is None or data[field] == '':
                        errors.append({
                            'field': field,
                            'message': f'{field} is required'
                        })
            
            if errors:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Validation failed',
                        'details': errors
                    }
                }), 422
            
            return f(data=data, *args, **kwargs)
        return decorated_function
    return decorator

def success_response(data=None, message=None, status_code=200):
    """Create success response"""
    response = {'success': True}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    return jsonify(response), status_code

def error_response(code, message, details=None, status_code=400):
    """Create error response"""
    response = {
        'success': False,
        'error': {
            'code': code,
            'message': message
        }
    }
    if details:
        response['error']['details'] = details
    return jsonify(response), status_code