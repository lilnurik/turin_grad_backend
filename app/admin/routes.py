from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from app.database import db, User, ActivityLog, Notification
from app.utils.decorators import (
    role_required, validate_json_data, success_response, error_response,
    get_pagination_params, create_pagination_response,
    validate_email_format, validate_phone_format, validate_student_id, validate_password
)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_users(current_user):
    """Get list of all users with filtering
    ---
    tags:
      - Admin
    summary: Получить список всех пользователей
    description: Возвращает пагинированный список всех пользователей с возможностью фильтрации
    security:
      - Bearer: []
    parameters:
      - in: query
        name: page
        type: integer
        description: Номер страницы для пагинации
        default: 1
      - in: query
        name: limit
        type: integer
        description: Количество элементов на странице
        default: 10
      - in: query
        name: search
        type: string
        description: Поиск по имени, фамилии, email или студенческому ID
      - in: query
        name: role
        type: string
        enum: [admin, teacher, student]
        description: Фильтр по роли пользователя
      - in: query
        name: faculty
        type: string
        description: Фильтр по факультету
      - in: query
        name: verified
        type: boolean
        description: Фильтр по статусу верификации
    responses:
      200:
        description: Список пользователей успешно получен
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                items:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: string
                      firstName:
                        type: string
                      lastName:
                        type: string
                      email:
                        type: string
                      role:
                        type: string
                      faculty:
                        type: string
                      isVerified:
                        type: boolean
                      createdAt:
                        type: string
                        format: date-time
                pagination:
                  type: object
                  properties:
                    page:
                      type: integer
                    limit:
                      type: integer
                    total:
                      type: integer
                    totalPages:
                      type: integer
      403:
        description: Доступ запрещен (только для администраторов)
    """
    page, limit = get_pagination_params()
    
    # Base query
    query = User.query
    
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
    
    role = request.args.get('role')
    if role:
        query = query.filter(User.role == role)
    
    faculty = request.args.get('faculty')
    if faculty:
        query = query.filter(User.faculty == faculty)
    
    verified = request.args.get('verified')
    if verified is not None:
        query = query.filter(User.is_verified == (verified.lower() == 'true'))
    
    # Sort by creation date (newest first)
    query = query.order_by(User.created_at.desc())
    
    return success_response(create_pagination_response(query, page, limit))

@admin_bp.route('/users/<user_id>', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_user(current_user, user_id):
    """Get detailed information about a user
    ---
    tags:
      - Admin
    summary: Получить детальную информацию о пользователе
    description: Возвращает подробную информацию о пользователе по ID
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
        description: ID пользователя
    responses:
      200:
        description: Информация о пользователе успешно получена
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                id:
                  type: string
                firstName:
                  type: string
                lastName:
                  type: string
                email:
                  type: string
                phone:
                  type: string
                role:
                  type: string
                faculty:
                  type: string
                studentId:
                  type: string
                isVerified:
                  type: boolean
                isBlocked:
                  type: boolean
                emailVerified:
                  type: boolean
                phoneVerified:
                  type: boolean
                createdAt:
                  type: string
                  format: date-time
                lastLogin:
                  type: string
                  format: date-time
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Пользователь не найден
    """
    user = User.query.get(user_id)
    if not user:
        return error_response('USER_NOT_FOUND', 'User not found', status_code=404)
    
    return success_response(user.to_dict())

@admin_bp.route('/users', methods=['POST'])
@jwt_required()
@role_required('admin')
@validate_json_data(required_fields=[
    'firstName', 'lastName', 'email', 'role', 'password'
])
def create_user(current_user, data):
    """Create a new user (admin only)
    ---
    tags:
      - Admin
    summary: Создать нового пользователя
    description: Создает нового пользователя в системе (только для администраторов)
    security:
      - Bearer: []
    parameters:
      - in: body
        name: user_data
        description: Данные нового пользователя
        required: true
        schema:
          type: object
          required:
            - firstName
            - lastName
            - email
            - role
            - password
          properties:
            firstName:
              type: string
              description: Имя пользователя
              example: "Иван"
            lastName:
              type: string
              description: Фамилия пользователя
              example: "Иванов"
            email:
              type: string
              description: Email адрес
              example: "ivan.ivanov@ttpu.uz"
            phone:
              type: string
              description: Номер телефона в формате +998XXXXXXXXX
              example: "+998901234567"
            studentId:
              type: string
              description: Студенческий ID (8 цифр, только для студентов)
              example: "12345678"
            role:
              type: string
              enum: [admin, teacher, student]
              description: Роль пользователя
              example: "student"
            password:
              type: string
              description: Пароль (минимум 8 символов)
              example: "password123"
            faculty:
              type: string
              description: Факультет
              example: "Engineering"
            direction:
              type: string
              description: Направление обучения
              example: "Computer Science"
    responses:
      201:
        description: Пользователь успешно создан
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                id:
                  type: string
                firstName:
                  type: string
                lastName:
                  type: string
                email:
                  type: string
                role:
                  type: string
                createdAt:
                  type: string
                  format: date-time
            message:
              type: string
              example: "User created successfully"
      400:
        description: Ошибка валидации данных
      403:
        description: Доступ запрещен (только для администраторов)
      409:
        description: Пользователь с таким email уже существует
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
    
    # Role validation
    if data['role'] not in ['admin', 'teacher', 'student']:
        errors.append({'field': 'role', 'message': 'Invalid role'})
    
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
        role=data['role'],
        faculty=data.get('faculty'),
        direction=data.get('direction'),
        is_verified=True,  # Admin-created users are auto-verified
        email_verified=True
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Log activity
    activity_log = ActivityLog(
        user_id=current_user.id,
        action='USER_CREATED',
        target_id=user.id,
        target_type='user',
        details=f'Created user {user.email} with role {user.role}',
        ip_address=request.environ.get('REMOTE_ADDR'),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(activity_log)
    db.session.commit()
    
    return success_response(user.to_dict(), status_code=201)

@admin_bp.route('/users/<user_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
@validate_json_data()
def update_user(current_user, data, user_id):
    """Update user information
    ---
    tags:
      - Admin
    summary: Обновить информацию пользователя
    description: Обновляет информацию о пользователе (только для администраторов)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
        description: ID пользователя
      - in: body
        name: user_data
        description: Данные для обновления пользователя
        required: true
        schema:
          type: object
          properties:
            firstName:
              type: string
              description: Имя пользователя
              example: "Иван"
            lastName:
              type: string
              description: Фамилия пользователя
              example: "Иванов"
            email:
              type: string
              description: Email адрес
              example: "ivan.ivanov@ttpu.uz"
            phone:
              type: string
              description: Номер телефона в формате +998XXXXXXXXX
              example: "+998901234567"
            studentId:
              type: string
              description: Студенческий ID (8 цифр)
              example: "12345678"
            faculty:
              type: string
              description: Факультет
              example: "Engineering"
            direction:
              type: string
              description: Направление обучения
              example: "Computer Science"
    responses:
      200:
        description: Информация пользователя успешно обновлена
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                id:
                  type: string
                firstName:
                  type: string
                lastName:
                  type: string
                email:
                  type: string
                phone:
                  type: string
                role:
                  type: string
                updatedAt:
                  type: string
                  format: date-time
            message:
              type: string
              example: "User updated successfully"
      400:
        description: Ошибка валидации данных
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Пользователь не найден
      409:
        description: Email или студенческий ID уже используется
    """
    user = User.query.get(user_id)
    if not user:
        return error_response('USER_NOT_FOUND', 'User not found', status_code=404)
    
    # Validate input data
    errors = []
    
    # Email validation (if being updated)
    if 'email' in data and data['email'] != user.email:
        if not validate_email_format(data['email']):
            errors.append({'field': 'email', 'message': 'Invalid email format'})
        
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            errors.append({'field': 'email', 'message': 'Email already registered'})
    
    # Phone validation (if being updated)
    if 'phone' in data and data['phone'] and data['phone'] != user.phone:
        if not validate_phone_format(data['phone']):
            errors.append({'field': 'phone', 'message': 'Invalid phone format'})
        
        existing_phone = User.query.filter_by(phone=data['phone']).first()
        if existing_phone:
            errors.append({'field': 'phone', 'message': 'Phone number already registered'})
    
    # Student ID validation (if being updated)
    if 'studentId' in data and data['studentId'] and data['studentId'] != user.student_id:
        if not validate_student_id(data['studentId']):
            errors.append({'field': 'studentId', 'message': 'Student ID must be 8 digits'})
        
        existing_student = User.query.filter_by(student_id=data['studentId']).first()
        if existing_student:
            errors.append({'field': 'studentId', 'message': 'Student ID already registered'})
    
    # Role validation (if being updated)
    if 'role' in data and data['role'] not in ['admin', 'teacher', 'student']:
        errors.append({'field': 'role', 'message': 'Invalid role'})
    
    if errors:
        return error_response('VALIDATION_ERROR', 'Validation failed', errors, 422)
    
    # Update user fields
    updatable_fields = [
        'firstName', 'lastName', 'middleName', 'email', 'phone', 'studentId',
        'role', 'faculty', 'direction', 'admissionYear', 'graduationYear', 'financingType'
    ]
    
    field_map = {
        'firstName': 'first_name',
        'lastName': 'last_name',
        'middleName': 'middle_name',
        'studentId': 'student_id',
        'admissionYear': 'admission_year',
        'graduationYear': 'graduation_year',
        'financingType': 'financing_type'
    }
    
    updated_fields = []
    for field in updatable_fields:
        if field in data:
            db_field = field_map.get(field, field)
            if hasattr(user, db_field):
                old_value = getattr(user, db_field)
                new_value = data[field]
                if old_value != new_value:
                    setattr(user, db_field, new_value)
                    updated_fields.append(field)
    
    if updated_fields:
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log activity
        activity_log = ActivityLog(
            user_id=current_user.id,
            action='USER_UPDATED',
            target_id=user.id,
            target_type='user',
            details=f'Updated user fields: {", ".join(updated_fields)}',
            ip_address=request.environ.get('REMOTE_ADDR'),
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(activity_log)
        db.session.commit()
    
    return success_response(user.to_dict())

@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_user(current_user, user_id):
    """Delete a user
    ---
    tags:
      - Admin
    summary: Удалить пользователя
    description: Удаляет пользователя из системы (только для администраторов)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
        description: ID пользователя для удаления
    responses:
      200:
        description: Пользователь успешно удален
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "User deleted successfully"
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Пользователь не найден
      400:
        description: Нельзя удалить самого себя
    """
    user = User.query.get(user_id)
    if not user:
        return error_response('USER_NOT_FOUND', 'User not found', status_code=404)
    
    if user.id == current_user.id:
        return error_response('CANNOT_DELETE_SELF', 'Cannot delete your own account', status_code=400)
    
    user_email = user.email
    db.session.delete(user)
    db.session.commit()
    
    # Log activity
    activity_log = ActivityLog(
        user_id=current_user.id,
        action='USER_DELETED',
        target_id=user_id,
        target_type='user',
        details=f'Deleted user {user_email}',
        ip_address=request.environ.get('REMOTE_ADDR'),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(activity_log)
    db.session.commit()
    
    return success_response(message='User deleted successfully')

@admin_bp.route('/users/<user_id>/verify', methods=['PATCH'])
@jwt_required()
@role_required('admin')
def verify_user(current_user, user_id):
    """Verify a user account
    ---
    tags:
      - Admin
    summary: Верифицировать аккаунт пользователя
    description: Административная верификация аккаунта пользователя
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
        description: ID пользователя для верификации
    responses:
      200:
        description: Пользователь успешно верифицирован
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                id:
                  type: string
                firstName:
                  type: string
                lastName:
                  type: string
                email:
                  type: string
                isVerified:
                  type: boolean
                  example: true
                verifiedAt:
                  type: string
                  format: date-time
            message:
              type: string
              example: "User verified successfully"
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Пользователь не найден
      400:
        description: Пользователь уже верифицирован
    """
    user = User.query.get(user_id)
    if not user:
        return error_response('USER_NOT_FOUND', 'User not found', status_code=404)
    
    if user.is_verified:
        return error_response('ALREADY_VERIFIED', 'User is already verified', status_code=400)
    
    user.is_verified = True
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Create notification for user
    notification = Notification(
        user_id=user.id,
        title='Аккаунт верифицирован',
        message='Ваш аккаунт был верифицирован администратором. Теперь вы можете использовать все функции системы.',
        type='success'
    )
    db.session.add(notification)
    
    # Log activity
    activity_log = ActivityLog(
        user_id=current_user.id,
        action='USER_VERIFIED',
        target_id=user.id,
        target_type='user',
        details=f'Verified user {user.email}',
        ip_address=request.environ.get('REMOTE_ADDR'),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(activity_log)
    db.session.commit()
    
    return success_response(user.to_dict(), message='User verified successfully')

@admin_bp.route('/users/<user_id>/block', methods=['PATCH'])
@jwt_required()
@role_required('admin')
@validate_json_data(required_fields=['blocked'])
def block_user(current_user, data, user_id):
    """Block or unblock a user
    ---
    tags:
      - Admin
    summary: Заблокировать или разблокировать пользователя
    description: Административная блокировка или разблокировка аккаунта пользователя
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: string
        required: true
        description: ID пользователя
      - in: body
        name: block_data
        description: Данные для блокировки/разблокировки
        required: true
        schema:
          type: object
          required:
            - blocked
          properties:
            blocked:
              type: boolean
              description: true для блокировки, false для разблокировки
              example: true
            reason:
              type: string
              description: Причина блокировки (опционально)
              example: "Нарушение правил"
    responses:
      200:
        description: Статус блокировки пользователя успешно изменен
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                id:
                  type: string
                firstName:
                  type: string
                lastName:
                  type: string
                email:
                  type: string
                isBlocked:
                  type: boolean
                  example: true
                blockedAt:
                  type: string
                  format: date-time
            message:
              type: string
              example: "User blocked successfully"
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Пользователь не найден
      400:
        description: Нельзя заблокировать самого себя
    """
    user = User.query.get(user_id)
    if not user:
        return error_response('USER_NOT_FOUND', 'User not found', status_code=404)
    
    if user.id == current_user.id:
        return error_response('CANNOT_BLOCK_SELF', 'Cannot block your own account', status_code=400)
    
    blocked = data['blocked']
    reason = data.get('reason', '') if blocked else None
    
    user.is_blocked = blocked
    user.block_reason = reason
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Create notification for user
    if blocked:
        notification = Notification(
            user_id=user.id,
            title='Аккаунт заблокирован',
            message=f'Ваш аккаунт был заблокирован. Причина: {reason}',
            type='error'
        )
    else:
        notification = Notification(
            user_id=user.id,
            title='Аккаунт разблокирован',
            message='Ваш аккаунт был разблокирован. Вы можете снова использовать систему.',
            type='success'
        )
    
    db.session.add(notification)
    
    # Log activity
    action = 'USER_BLOCKED' if blocked else 'USER_UNBLOCKED'
    details = f'{"Blocked" if blocked else "Unblocked"} user {user.email}'
    if blocked and reason:
        details += f' with reason: {reason}'
    
    activity_log = ActivityLog(
        user_id=current_user.id,
        action=action,
        target_id=user.id,
        target_type='user',
        details=details,
        ip_address=request.environ.get('REMOTE_ADDR'),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(activity_log)
    db.session.commit()
    
    action_text = 'blocked' if blocked else 'unblocked'
    return success_response(user.to_dict(), message=f'User {action_text} successfully')

@admin_bp.route('/activity-logs', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_activity_logs(current_user):
    """Get activity logs
    ---
    tags:
      - Admin
    summary: Получить журнал активности
    description: Возвращает пагинированный список всех действий пользователей в системе
    security:
      - Bearer: []
    parameters:
      - in: query
        name: page
        type: integer
        description: Номер страницы для пагинации
        default: 1
      - in: query
        name: limit
        type: integer
        description: Количество элементов на странице
        default: 10
      - in: query
        name: user_id
        type: string
        description: Фильтр по ID пользователя
      - in: query
        name: action
        type: string
        description: Фильтр по типу действия
        enum: [USER_LOGIN, USER_LOGOUT, USER_REGISTERED, EMAIL_VERIFIED, PHONE_VERIFIED, PASSWORD_RESET_COMPLETED, USER_CREATED, USER_UPDATED, USER_DELETED, USER_VERIFIED, USER_BLOCKED, USER_UNBLOCKED]
    responses:
      200:
        description: Журнал активности успешно получен
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                items:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: string
                      userId:
                        type: string
                      action:
                        type: string
                      details:
                        type: string
                      ipAddress:
                        type: string
                      userAgent:
                        type: string
                      createdAt:
                        type: string
                        format: date-time
                      user:
                        type: object
                        properties:
                          firstName:
                            type: string
                          lastName:
                            type: string
                          email:
                            type: string
                pagination:
                  type: object
                  properties:
                    page:
                      type: integer
                    limit:
                      type: integer
                    total:
                      type: integer
                    totalPages:
                      type: integer
      403:
        description: Доступ запрещен (только для администраторов)
    """
    page, limit = get_pagination_params()
    
    # Base query
    query = ActivityLog.query
    
    # Apply filters
    user_id = request.args.get('userId')
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    
    action = request.args.get('action')
    if action:
        query = query.filter(ActivityLog.action == action)
    
    start_date = request.args.get('startDate')
    if start_date:
        try:
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(ActivityLog.created_at >= start_date)
        except ValueError:
            pass
    
    end_date = request.args.get('endDate')
    if end_date:
        try:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(ActivityLog.created_at <= end_date)
        except ValueError:
            pass
    
    # Sort by creation date (newest first)
    query = query.order_by(ActivityLog.created_at.desc())
    
    return success_response(create_pagination_response(query, page, limit))