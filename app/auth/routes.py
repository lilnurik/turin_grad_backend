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
    """User login endpoint
    ---
    tags:
      - Authentication
    summary: Аутентификация пользователя
    description: Вход в систему по email, телефону или студенческому ID
    parameters:
      - in: body
        name: credentials
        description: Данные для входа
        required: true
        schema:
          type: object
          required:
            - identifier
            - password
          properties:
            identifier:
              type: string
              description: Email, телефон (+998901234567) или студенческий ID
              example: "admin@ttpu.uz"
            password:
              type: string
              description: Пароль пользователя
              example: "admin123"
    responses:
      200:
        description: Успешная аутентификация
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                user:
                  type: object
                  properties:
                    id:
                      type: string
                      example: "user_id"
                    firstName:
                      type: string
                      example: "Имя"
                    lastName:
                      type: string
                      example: "Фамилия"
                    email:
                      type: string
                      example: "admin@ttpu.uz"
                    role:
                      type: string
                      enum: ["admin", "teacher", "student"]
                      example: "admin"
                    avatar:
                      type: string
                      example: "avatar_url"
                    lastLogin:
                      type: string
                      format: date-time
                      example: "2025-01-15T08:00:00Z"
                token:
                  type: string
                  description: JWT access token
                  example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                refreshToken:
                  type: string
                  description: JWT refresh token
                  example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
      401:
        description: Неверные учетные данные
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: "INVALID_CREDENTIALS"
                message:
                  type: string
                  example: "Invalid credentials"
      403:
        description: Аккаунт заблокирован
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: "USER_BLOCKED"
                message:
                  type: string
                  example: "Account is blocked: reason"
    """
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
    """User logout endpoint
    ---
    tags:
      - Authentication
    summary: Выход из системы
    description: Выход пользователя из системы с аннулированием токена
    security:
      - Bearer: []
    parameters:
      - in: body
        name: logout_data
        description: Данные для выхода
        required: true
        schema:
          type: object
          required:
            - refreshToken
          properties:
            refreshToken:
              type: string
              description: Refresh token для аннулирования
              example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    responses:
      200:
        description: Успешный выход из системы
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Successfully logged out"
      401:
        description: Не авторизован
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: "UNAUTHORIZED"
                message:
                  type: string
                  example: "Unauthorized access"
    """
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
    """User registration endpoint
    ---
    tags:
      - Authentication
    summary: Регистрация нового пользователя
    description: Регистрация нового студента в системе
    parameters:
      - in: body
        name: registration_data
        description: Данные для регистрации
        required: true
        schema:
          type: object
          required:
            - firstName
            - lastName
            - email
            - password
            - faculty
            - direction
          properties:
            firstName:
              type: string
              description: Имя пользователя
              example: "Алишер"
            lastName:
              type: string
              description: Фамилия пользователя
              example: "Рахмонов"
            middleName:
              type: string
              description: Отчество (необязательно)
              example: "Абдуллаевич"
            email:
              type: string
              format: email
              description: Email адрес
              example: "a.rahmonov@student.ttpu.uz"
            phone:
              type: string
              description: Номер телефона (необязательно)
              example: "+998901234567"
            studentId:
              type: string
              description: Студенческий ID (необязательно)
              example: "12345678"
            password:
              type: string
              description: Пароль (минимум 8 символов)
              example: "password123"
            faculty:
              type: string
              description: Факультет
              example: "Информационные технологии"
            direction:
              type: string
              description: Направление обучения
              example: "Программная инженерия"
    responses:
      201:
        description: Пользователь успешно зарегистрирован
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Registration successful. Please verify your email."
            data:
              type: object
              properties:
                userId:
                  type: string
                  example: "user_id"
      400:
        description: Ошибка валидации данных
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: "VALIDATION_ERROR"
                message:
                  type: string
                  example: "Validation failed"
                details:
                  type: array
                  items:
                    type: object
                    properties:
                      field:
                        type: string
                        example: "email"
                      message:
                        type: string
                        example: "Invalid email format"
      409:
        description: Пользователь уже существует
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: "USER_EXISTS"
                message:
                  type: string
                  example: "User already exists"
    """
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
    """Email verification endpoint
    ---
    tags:
      - Authentication
    summary: Верификация email адреса
    description: Подтверждение email адреса пользователя с помощью токена верификации
    parameters:
      - in: body
        name: verification_data
        description: Данные для верификации email
        required: true
        schema:
          type: object
          required:
            - token
          properties:
            token:
              type: string
              description: Токен верификации email
              example: "abc123def456"
    responses:
      200:
        description: Email успешно верифицирован
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Email verified successfully"
      400:
        description: Неверный или просроченный токен
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: "INVALID_TOKEN"
                message:
                  type: string
                  example: "Invalid or expired verification token"
    """
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
    """Send SMS verification code
    ---
    tags:
      - Authentication
    summary: Отправка SMS кода верификации
    description: Отправляет SMS код верификации на указанный номер телефона
    parameters:
      - in: body
        name: sms_data
        description: Данные для отправки SMS
        required: true
        schema:
          type: object
          required:
            - phone
          properties:
            phone:
              type: string
              description: Номер телефона в формате +998XXXXXXXXX
              example: "+998901234567"
    responses:
      200:
        description: SMS код успешно отправлен
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "SMS code sent successfully"
      400:
        description: Неверный формат номера телефона
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: "INVALID_PHONE"
                message:
                  type: string
                  example: "Invalid phone number format"
      500:
        description: Ошибка отправки SMS
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: "SMS_SEND_FAILED"
                message:
                  type: string
                  example: "Failed to send SMS code"
    """
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
    """Verify SMS code
    ---
    tags:
      - Authentication
    summary: Верификация SMS кода
    description: Проверяет SMS код верификации для указанного номера телефона
    parameters:
      - in: body
        name: verification_data
        description: Данные для верификации SMS кода
        required: true
        schema:
          type: object
          required:
            - phone
            - code
          properties:
            phone:
              type: string
              description: Номер телефона в формате +998XXXXXXXXX
              example: "+998901234567"
            code:
              type: string
              description: SMS код верификации
              example: "123456"
    responses:
      200:
        description: SMS код успешно верифицирован
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Phone verified successfully"
      400:
        description: Неверный или просроченный SMS код
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: "INVALID_CODE"
                message:
                  type: string
                  example: "Invalid or expired SMS code"
    """
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
    """Refresh access token
    ---
    tags:
      - Authentication
    summary: Обновление access токена
    description: Генерирует новый access токен используя refresh токен
    security:
      - Bearer: []
    responses:
      200:
        description: Новый access токен успешно создан
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                token:
                  type: string
                  description: Новый JWT access токен
                  example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
      401:
        description: Пользователь не найден или заблокирован
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: "USER_NOT_FOUND"
                message:
                  type: string
                  example: "User not found or blocked"
    """
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
    """Request password reset
    ---
    tags:
      - Authentication
    summary: Запрос сброса пароля
    description: Отправляет email с ссылкой для сброса пароля
    parameters:
      - in: body
        name: reset_request
        description: Данные для запроса сброса пароля
        required: true
        schema:
          type: object
          required:
            - identifier
          properties:
            identifier:
              type: string
              description: Email или номер телефона пользователя
              example: "user@example.com"
    responses:
      200:
        description: Если аккаунт существует, будет отправлен email для сброса пароля
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "If the account exists, a password reset email will be sent"
    """
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
    """Reset password with token
    ---
    tags:
      - Authentication
    summary: Сброс пароля по токену
    description: Устанавливает новый пароль используя токен сброса
    parameters:
      - in: body
        name: reset_data
        description: Данные для сброса пароля
        required: true
        schema:
          type: object
          required:
            - token
            - newPassword
          properties:
            token:
              type: string
              description: Токен сброса пароля
              example: "reset-token-123"
            newPassword:
              type: string
              description: Новый пароль (минимум 8 символов)
              example: "newPassword123"
    responses:
      200:
        description: Пароль успешно сброшен
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Password reset successfully"
      400:
        description: Неверный токен или пароль
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: "INVALID_TOKEN"
                message:
                  type: string
                  example: "Invalid or expired reset token"
    """
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