from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from datetime import datetime, timedelta
from app.database import db, User, ActivityLog
from app.utils.decorators import validate_json_data, success_response, error_response
from app.utils.email import (
    send_verification_email, send_password_reset_email, 
    send_admin_verification_request, generate_sms_code, 
    send_sms_code, store_sms_code, verify_sms_code
)
from app.utils.decorators import (
    validate_email_format, validate_phone_format, 
    validate_student_id, validate_password
)

auth_bp = Blueprint('auth', __name__)

# Token blacklist for logout
blacklisted_tokens = set()

@auth_bp.route('/login', methods=['POST'])
@validate_json_data(required_fields=['identifier', 'password'])
def login(data):
    """User login endpoint"""
    identifier = data['identifier'].strip()
    password = data['password']
    
    # Find user by email, phone, or student ID
    user = None
    if '@' in identifier:
        user = User.query.filter_by(email=identifier).first()
    elif identifier.startswith('+'):
        user = User.query.filter_by(phone=identifier).first()
    else:
        user = User.query.filter_by(student_id=identifier).first()
    
    if not user or not user.check_password(password):
        return error_response('INVALID_CREDENTIALS', 'Invalid credentials', status_code=401)
    
    if user.is_blocked:
        return error_response('USER_BLOCKED', f'Account is blocked: {user.block_reason}', status_code=403)
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    # Log activity
    activity_log = ActivityLog(
        user_id=user.id,
        action='USER_LOGIN',
        details=f'User logged in via {identifier}',
        ip_address=request.environ.get('REMOTE_ADDR'),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(activity_log)
    db.session.commit()
    
    return success_response({
        'user': user.to_dict(),
        'token': access_token,
        'refreshToken': refresh_token
    })

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
@validate_json_data(required_fields=['refreshToken'])
def logout(data):
    """User logout endpoint"""
    current_user_id = get_jwt_identity()
    jti = get_jwt()['jti']
    
    # Add token to blacklist
    blacklisted_tokens.add(jti)
    
    # Log activity
    activity_log = ActivityLog(
        user_id=current_user_id,
        action='USER_LOGOUT',
        details='User logged out',
        ip_address=request.environ.get('REMOTE_ADDR'),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(activity_log)
    db.session.commit()
    
    return success_response(message='Successfully logged out')

@auth_bp.route('/register', methods=['POST'])
@validate_json_data(required_fields=[
    'firstName', 'lastName', 'email', 'password', 'faculty', 'direction'
])
def register(data):
    """User registration endpoint"""
    # Validate input data
    errors = []
    
    # Email validation
    if not validate_email_format(data['email']):
        errors.append({'field': 'email', 'message': 'Invalid email format'})
    
    # Phone validation (if provided)
    if 'phone' in data and data['phone']:
        if not validate_phone_format(data['phone']):
            errors.append({'field': 'phone', 'message': 'Invalid phone format'})
    
    # Student ID validation (if provided)
    if 'studentId' in data and data['studentId']:
        if not validate_student_id(data['studentId']):
            errors.append({'field': 'studentId', 'message': 'Student ID must be 8 digits'})
    
    # Password validation
    is_valid_password, password_error = validate_password(data['password'])
    if not is_valid_password:
        errors.append({'field': 'password', 'message': password_error})
    
    # Check for existing users
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        errors.append({'field': 'email', 'message': 'Email already registered'})
    
    if 'phone' in data and data['phone']:
        existing_phone = User.query.filter_by(phone=data['phone']).first()
        if existing_phone:
            errors.append({'field': 'phone', 'message': 'Phone number already registered'})
    
    if 'studentId' in data and data['studentId']:
        existing_student = User.query.filter_by(student_id=data['studentId']).first()
        if existing_student:
            errors.append({'field': 'studentId', 'message': 'Student ID already registered'})
    
    if errors:
        return error_response('VALIDATION_ERROR', 'Validation failed', errors, 422)
    
    # Create new user
    user = User(
        first_name=data['firstName'],
        last_name=data['lastName'],
        middle_name=data.get('middleName'),
        email=data['email'],
        phone=data.get('phone'),
        student_id=data.get('studentId'),
        faculty=data['faculty'],
        direction=data['direction'],
        role='student'  # Default role
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Send verification email
    if send_verification_email(user):
        db.session.commit()  # Save the verification token
    
    # Notify admins about new registration
    send_admin_verification_request(user)
    
    # Log activity
    activity_log = ActivityLog(
        user_id=user.id,
        action='USER_REGISTERED',
        details='New user registered',
        ip_address=request.environ.get('REMOTE_ADDR'),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(activity_log)
    db.session.commit()
    
    return success_response({
        'user': user.to_dict(),
        'message': 'Registration successful. Please check your email for verification.'
    }, status_code=201)

@auth_bp.route('/verify-email', methods=['POST'])
@validate_json_data(required_fields=['token'])
def verify_email(data):
    """Email verification endpoint"""
    token = data['token']
    
    user = User.query.filter_by(email_verification_token=token).first()
    if not user:
        return error_response('INVALID_TOKEN', 'Invalid or expired verification token', status_code=400)
    
    user.email_verified = True
    user.email_verification_token = None
    db.session.commit()
    
    # Log activity
    activity_log = ActivityLog(
        user_id=user.id,
        action='EMAIL_VERIFIED',
        details='Email address verified',
        ip_address=request.environ.get('REMOTE_ADDR'),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(activity_log)
    db.session.commit()
    
    return success_response(message='Email verified successfully')

@auth_bp.route('/send-sms', methods=['POST'])
@validate_json_data(required_fields=['phone'])
def send_sms(data):
    """Send SMS verification code"""
    phone = data['phone']
    
    if not validate_phone_format(phone):
        return error_response('INVALID_PHONE', 'Invalid phone number format', status_code=400)
    
    # Generate and send SMS code
    code = generate_sms_code()
    store_sms_code(phone, code)  # Store for verification
    
    if send_sms_code(phone, code):
        return success_response(message='SMS code sent successfully')
    else:
        return error_response('SMS_SEND_FAILED', 'Failed to send SMS code', status_code=500)

@auth_bp.route('/verify-sms', methods=['POST'])
@validate_json_data(required_fields=['phone', 'code'])
def verify_sms(data):
    """Verify SMS code"""
    phone = data['phone']
    code = data['code']
    
    if verify_sms_code(phone, code):
        # Update user phone verification status
        user = User.query.filter_by(phone=phone).first()
        if user:
            user.phone_verified = True
            db.session.commit()
            
            # Log activity
            activity_log = ActivityLog(
                user_id=user.id,
                action='PHONE_VERIFIED',
                details='Phone number verified',
                ip_address=request.environ.get('REMOTE_ADDR'),
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(activity_log)
            db.session.commit()
        
        return success_response(message='Phone verified successfully')
    else:
        return error_response('INVALID_CODE', 'Invalid or expired SMS code', status_code=400)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    
    # Check if user still exists and is not blocked
    user = User.query.get(current_user_id)
    if not user or user.is_blocked:
        return error_response('USER_NOT_FOUND', 'User not found or blocked', status_code=401)
    
    new_token = create_access_token(identity=current_user_id)
    
    return success_response({
        'token': new_token
    })

@auth_bp.route('/forgot-password', methods=['POST'])
@validate_json_data(required_fields=['identifier'])
def forgot_password(data):
    """Request password reset"""
    identifier = data['identifier'].strip()
    
    # Find user by email or phone
    user = None
    if '@' in identifier:
        user = User.query.filter_by(email=identifier).first()
    else:
        user = User.query.filter_by(phone=identifier).first()
    
    if not user:
        # Don't reveal whether user exists
        return success_response(message='If the account exists, a password reset email will be sent')
    
    if user.is_blocked:
        return error_response('USER_BLOCKED', 'Account is blocked', status_code=403)
    
    # Send password reset email
    if send_password_reset_email(user):
        db.session.commit()  # Save the reset token
        
        # Log activity
        activity_log = ActivityLog(
            user_id=user.id,
            action='PASSWORD_RESET_REQUESTED',
            details='Password reset requested',
            ip_address=request.environ.get('REMOTE_ADDR'),
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(activity_log)
        db.session.commit()
    
    return success_response(message='If the account exists, a password reset email will be sent')

@auth_bp.route('/reset-password', methods=['POST'])
@validate_json_data(required_fields=['token', 'newPassword'])
def reset_password(data):
    """Reset password with token"""
    token = data['token']
    new_password = data['newPassword']
    
    # Validate new password
    is_valid_password, password_error = validate_password(new_password)
    if not is_valid_password:
        return error_response('INVALID_PASSWORD', password_error, status_code=400)
    
    # Find user with valid reset token
    user = User.query.filter(
        User.password_reset_token == token,
        User.password_reset_expires > datetime.utcnow()
    ).first()
    
    if not user:
        return error_response('INVALID_TOKEN', 'Invalid or expired reset token', status_code=400)
    
    # Update password
    user.set_password(new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    db.session.commit()
    
    # Log activity
    activity_log = ActivityLog(
        user_id=user.id,
        action='PASSWORD_RESET_COMPLETED',
        details='Password reset completed',
        ip_address=request.environ.get('REMOTE_ADDR'),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(activity_log)
    db.session.commit()
    
    return success_response(message='Password reset successfully')

# JWT token blacklist check
@auth_bp.before_app_request
def check_if_token_revoked():
    try:
        jti = get_jwt().get('jti')
        if jti in blacklisted_tokens:
            return error_response('TOKEN_REVOKED', 'Token has been revoked', status_code=401)
    except:
        pass  # No token in request