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
    """Get list of all users with filtering (Admin only)
    ---
    tags:
      - Admin - Users
    summary: Получить список всех пользователей (для администраторов)
    description: Возвращает пагинированный список всех пользователей с возможностью фильтрации. Для CRUD операций используйте специальные endpoints для студентов и преподавателей.
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

@admin_bp.route('/graduating-students', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_graduating_students(current_user):
    """Get list of students eligible for graduation
    ---
    tags:
      - Admin
    summary: Получить список студентов готовых к выпуску
    description: Возвращает список студентов, которые готовы к выпуску (текущий год >= год выпуска)
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
        name: faculty
        type: string
        description: Фильтр по факультету
      - in: query
        name: degreeLevel
        type: string
        enum: [bachelor, master, phd, dsc]
        description: Фильтр по уровню образования
    responses:
      200:
        description: Список студентов готовых к выпуску успешно получен
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
                      studentId:
                        type: string
                      faculty:
                        type: string
                      direction:
                        type: string
                      admissionYear:
                        type: integer
                      graduationYear:
                        type: integer
                      academicYearPeriod:
                        type: string
                        example: "06.2021-06.2025"
                      degreeLevel:
                        type: string
                      studentType:
                        type: string
                      isEligibleForGraduation:
                        type: boolean
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
    
    # Query students who are eligible for graduation
    query = User.query.filter(
        User.role == 'student',
        User.student_status == 'current',
        User.graduation_year.isnot(None)
    )
    
    # Filter by faculty if provided
    faculty = request.args.get('faculty')
    if faculty:
        query = query.filter(User.faculty == faculty)
    
    # Filter by degree level if provided
    degree_level = request.args.get('degreeLevel')
    if degree_level:
        query = query.filter(User.degree_level == degree_level)
    
    # Filter only eligible students (graduation year <= current academic year)
    from datetime import datetime
    current_date = datetime.now()
    current_academic_year = current_date.year
    if current_date.month < 6:  # Before June, still in previous academic year
        current_academic_year -= 1
    
    query = query.filter(User.graduation_year <= current_academic_year + 1)
    
    # Sort by graduation year and last name
    query = query.order_by(User.graduation_year.asc(), User.last_name.asc())
    
    return success_response(create_pagination_response(query, page, limit))

@admin_bp.route('/students/<student_id>/confirm-graduation', methods=['POST'])
@jwt_required()
@role_required('admin')
def confirm_graduation(current_user, student_id):
    """Confirm student graduation
    ---
    tags:
      - Admin
    summary: Подтвердить выпуск студента
    description: Изменяет статус студента на "выпускник"
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        type: string
        required: true
        description: ID студента
    responses:
      200:
        description: Выпуск студента успешно подтвержден
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
                studentStatus:
                  type: string
                  example: "graduate"
      400:
        description: Ошибка валидации
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Студент не найден
    """
    # Find the student
    student = User.query.filter_by(id=student_id, role='student').first()
    if not student:
        return error_response('STUDENT_NOT_FOUND', 'Студент не найден', 404)
    
    # Check if student is eligible for graduation
    if not student.is_eligible_for_graduation():
        return error_response('NOT_ELIGIBLE', 'Студент не готов к выпуску', 400)
    
    if student.student_status == 'graduate':
        return error_response('ALREADY_GRADUATED', 'Студент уже выпущен', 400)
    
    # Validate graduation data
    validation_errors = student.validate_graduation_data()
    if validation_errors:
        return error_response('VALIDATION_ERROR', f'Ошибки валидации: {", ".join(validation_errors)}', 400)
    
    # Update student status
    student.student_status = 'graduate'
    student.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # Log the action
        log = ActivityLog(
            user_id=current_user.id,
            action='STUDENT_GRADUATED',
            target_id=student.id,
            target_type='User',
            details=f'Подтвержден выпуск студента {student.first_name} {student.last_name}'
        )
        db.session.add(log)
        
        # Create notification for the student
        notification = Notification(
            user_id=student.id,
            title='Поздравляем с выпуском!',
            message=f'Ваш выпуск был подтвержден администратором. Поздравляем с завершением обучения!',
            type='success'
        )
        db.session.add(notification)
        
        db.session.commit()
        
        return success_response(student.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return error_response('DATABASE_ERROR', 'Ошибка при обновлении статуса студента', 500)

@admin_bp.route('/students/<student_id>/revert-graduation', methods=['POST'])
@jwt_required()
@role_required('admin')
def revert_graduation(current_user, student_id):
    """Revert student graduation status
    ---
    tags:
      - Admin
    summary: Отменить выпуск студента
    description: Возвращает статус студента обратно на "действующий студент"
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        type: string
        required: true
        description: ID студента
    responses:
      200:
        description: Статус студента успешно изменен
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
                studentStatus:
                  type: string
                  example: "current"
      400:
        description: Ошибка валидации
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Студент не найден
    """
    # Find the student
    student = User.query.filter_by(id=student_id, role='student').first()
    if not student:
        return error_response('STUDENT_NOT_FOUND', 'Студент не найден', 404)
    
    if student.student_status != 'graduate':
        return error_response('NOT_GRADUATED', 'Студент не является выпускником', 400)
    
    # Update student status
    student.student_status = 'current'
    student.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # Log the action
        log = ActivityLog(
            user_id=current_user.id,
            action='STUDENT_GRADUATION_REVERTED',
            target_id=student.id,
            target_type='User',
            details=f'Отменен выпуск студента {student.first_name} {student.last_name}'
        )
        db.session.add(log)
        
        # Create notification for the student
        notification = Notification(
            user_id=student.id,
            title='Статус выпуска изменен',
            message=f'Ваш статус выпуска был изменен администратором.',
            type='info'
        )
        db.session.add(notification)
        
        db.session.commit()
        
        return success_response(student.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return error_response('DATABASE_ERROR', 'Ошибка при обновлении статуса студента', 500)
@admin_bp.route('/students/<student_id>/graduation-info', methods=['PUT'])
@jwt_required()
@role_required('admin')
@validate_json_data(required_fields=['admissionYear', 'graduationYear', 'degreeLevel'])
def update_graduation_info(current_user, student_id, data):
    """Update student graduation information
    ---
    tags:
      - Admin
    summary: Обновить информацию об обучении студента
    description: Обновляет годы поступления и выпуска, уровень образования и тип студента
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        type: string
        required: true
        description: ID студента
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - admissionYear
            - graduationYear
            - degreeLevel
          properties:
            admissionYear:
              type: integer
              example: 2021
              description: Год поступления
            graduationYear:
              type: integer
              example: 2025
              description: Год выпуска
            degreeLevel:
              type: string
              enum: [bachelor, master, phd, dsc]
              example: bachelor
              description: Уровень образования
            studentType:
              type: string
              enum: [regular, free_applicant, external]
              example: regular
              description: Тип студента (только для PhD/DSc)
            faculty:
              type: string
              example: "Факультет информатики"
              description: Факультет
            direction:
              type: string
              example: "Программная инженерия"
              description: Направление
    responses:
      200:
        description: Информация об обучении успешно обновлена
      400:
        description: Ошибка валидации
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Студент не найден
    """
    # Find the student
    student = User.query.filter_by(id=student_id, role='student').first()
    if not student:
        return error_response('STUDENT_NOT_FOUND', 'Студент не найден', 404)
    
    # Don't allow modification of graduated students without explicit permission
    if student.student_status == 'graduate':
        return error_response('STUDENT_GRADUATED', 'Нельзя изменить данные выпускника', 400)
    
    # Update fields
    old_graduation_year = student.graduation_year
    student.admission_year = data['admissionYear']
    student.graduation_year = data['graduationYear']
    student.degree_level = data['degreeLevel']
    
    if 'studentType' in data:
        student.student_type = data['studentType']
    elif data['degreeLevel'] in ['bachelor', 'master']:
        student.student_type = 'regular'  # Force regular for bachelor/master
    
    if 'faculty' in data:
        student.faculty = data['faculty']
    
    if 'direction' in data:
        student.direction = data['direction']
    
    # Validate the updated data
    validation_errors = student.validate_graduation_data()
    if validation_errors:
        return error_response('VALIDATION_ERROR', f'Ошибки валидации: {", ".join(validation_errors)}', 400)
    
    student.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # Log the action
        changes = []
        if old_graduation_year != data['graduationYear']:
            changes.append(f"год выпуска: {old_graduation_year} → {data['graduationYear']}")
        
        log = ActivityLog(
            user_id=current_user.id,
            action='STUDENT_GRADUATION_INFO_UPDATED',
            target_id=student.id,
            target_type='User',
            details=f'Обновлена информация об обучении студента {student.first_name} {student.last_name}. Изменения: {", ".join(changes) if changes else "данные обновлены"}'
        )
        db.session.add(log)
        
        # Create notification for the student
        notification = Notification(
            user_id=student.id,
            title='Обновлена информация об обучении',
            message=f'Администратор обновил информацию о вашем обучении.',
            type='info'
        )
        db.session.add(notification)
        
        db.session.commit()
        
        return success_response(student.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return error_response('DATABASE_ERROR', 'Ошибка при обновлении информации об обучении', 500)

@admin_bp.route('/graduation-statistics', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_graduation_statistics(current_user):
    """Get graduation statistics
    ---
    tags:
      - Admin
    summary: Получить статистику по выпускникам
    description: Возвращает статистику по студентам и выпускникам
    security:
      - Bearer: []
    parameters:
      - in: query
        name: year
        type: integer
        description: Год выпуска для фильтрации (по умолчанию текущий академический год)
    responses:
      200:
        description: Статистика успешно получена
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                currentStudents:
                  type: integer
                  description: Количество действующих студентов
                graduates:
                  type: integer
                  description: Количество выпускников
                eligibleForGraduation:
                  type: integer
                  description: Количество студентов готовых к выпуску
                byDegreeLevel:
                  type: object
                  properties:
                    bachelor:
                      type: object
                      properties:
                        current:
                          type: integer
                        graduates:
                          type: integer
                    master:
                      type: object
                      properties:
                        current:
                          type: integer
                        graduates:
                          type: integer
                    phd:
                      type: object
                      properties:
                        current:
                          type: integer
                        graduates:
                          type: integer
                    dsc:
                      type: object
                      properties:
                        current:
                          type: integer
                        graduates:
                          type: integer
                byFaculty:
                  type: object
                  description: Статистика по факультетам
      403:
        description: Доступ запрещен (только для администраторов)
    """
    from datetime import datetime
    from sqlalchemy import func
    
    # Get filter year
    filter_year = request.args.get('year', type=int)
    current_date = datetime.now()
    current_academic_year = current_date.year
    if current_date.month < 6:  # Before June, still in previous academic year
        current_academic_year -= 1
    
    if not filter_year:
        filter_year = current_academic_year + 1  # Default to current graduation year
    
    # Base statistics
    total_students = User.query.filter_by(role='student').count()
    current_students = User.query.filter_by(role='student', student_status='current').count()
    graduates = User.query.filter_by(role='student', student_status='graduate').count()
    
    # Students eligible for graduation
    eligible_query = User.query.filter(
        User.role == 'student',
        User.student_status == 'current',
        User.graduation_year <= current_academic_year + 1
    )
    eligible_for_graduation = eligible_query.count()
    
    # Statistics by degree level
    degree_stats = {}
    for degree in ['bachelor', 'master', 'phd', 'dsc']:
        current_count = User.query.filter_by(
            role='student', 
            student_status='current', 
            degree_level=degree
        ).count()
        graduate_count = User.query.filter_by(
            role='student', 
            student_status='graduate', 
            degree_level=degree
        ).count()
        
        degree_stats[degree] = {
            'current': current_count,
            'graduates': graduate_count
        }
    
    # Statistics by faculty
    faculty_stats = {}
    faculties = db.session.query(User.faculty).filter(
        User.role == 'student',
        User.faculty.isnot(None)
    ).distinct().all()
    
    for (faculty,) in faculties:
        current_count = User.query.filter_by(
            role='student', 
            student_status='current', 
            faculty=faculty
        ).count()
        graduate_count = User.query.filter_by(
            role='student', 
            student_status='graduate', 
            faculty=faculty
        ).count()
        
        faculty_stats[faculty] = {
            'current': current_count,
            'graduates': graduate_count
        }
    
    return success_response({
        'totalStudents': total_students,
        'currentStudents': current_students,
        'graduates': graduates,
        'eligibleForGraduation': eligible_for_graduation,
        'academicYear': f"06.{current_academic_year}-06.{current_academic_year + 1}",
        'byDegreeLevel': degree_stats,
        'byFaculty': faculty_stats
    })

# ========== STUDENT CRUD ENDPOINTS ==========

@admin_bp.route('/students', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_admin_students(current_user):
    """Get list of all students with filtering (Admin only)
    ---
    tags:
      - Admin - Students
    summary: Получить список всех студентов (для администраторов)
    description: Возвращает пагинированный список всех студентов с возможностью фильтрации
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
        name: faculty
        type: string
        description: Фильтр по факультету
      - in: query
        name: studentStatus
        type: string
        enum: [current, graduate]
        description: Фильтр по статусу студента
      - in: query
        name: degreeLevel
        type: string
        enum: [bachelor, master, phd, dsc]
        description: Фильтр по уровню образования
      - in: query
        name: verified
        type: boolean
        description: Фильтр по статусу верификации
    responses:
      200:
        description: Список студентов успешно получен
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
                      studentId:
                        type: string
                      faculty:
                        type: string
                      direction:
                        type: string
                      degreeLevel:
                        type: string
                      studentStatus:
                        type: string
                      admissionYear:
                        type: integer
                      graduationYear:
                        type: integer
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
    
    # Base query for students only
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
    
    student_status = request.args.get('studentStatus')
    if student_status:
        query = query.filter(User.student_status == student_status)
    
    degree_level = request.args.get('degreeLevel')
    if degree_level:
        query = query.filter(User.degree_level == degree_level)
    
    verified = request.args.get('verified')
    if verified is not None:
        query = query.filter(User.is_verified == (verified.lower() == 'true'))
    
    # Sort by creation date (newest first)
    query = query.order_by(User.created_at.desc())
    
    return success_response(create_pagination_response(query, page, limit))

@admin_bp.route('/students/<student_id>', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_admin_student(current_user, student_id):
    """Get detailed information about a student (Admin only)
    ---
    tags:
      - Admin - Students
    summary: Получить детальную информацию о студенте (для администраторов)
    description: Возвращает подробную информацию о студенте по ID
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        type: string
        required: true
        description: ID студента
    responses:
      200:
        description: Информация о студенте успешно получена
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
                studentId:
                  type: string
                faculty:
                  type: string
                direction:
                  type: string
                degreeLevel:
                  type: string
                studentStatus:
                  type: string
                studentType:
                  type: string
                admissionYear:
                  type: integer
                graduationYear:
                  type: integer
                financingType:
                  type: string
                isVerified:
                  type: boolean
                isBlocked:
                  type: boolean
                createdAt:
                  type: string
                  format: date-time
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Студент не найден
    """
    student = User.query.filter_by(id=student_id, role='student').first()
    if not student:
        return error_response('STUDENT_NOT_FOUND', 'Student not found', status_code=404)
    
    return success_response(student.to_dict())

@admin_bp.route('/students', methods=['POST'])
@jwt_required()
@role_required('admin')
@validate_json_data(required_fields=[
    'firstName', 'lastName', 'email', 'password', 'studentId', 'degreeLevel'
])
def create_admin_student(current_user, data):
    """Create a new student (Admin only)
    ---
    tags:
      - Admin - Students
    summary: Создать нового студента (для администраторов)
    description: Создает нового студента в системе
    security:
      - Bearer: []
    parameters:
      - in: body
        name: student_data
        description: Данные нового студента
        required: true
        schema:
          type: object
          required:
            - firstName
            - lastName
            - email
            - password
            - studentId
            - degreeLevel
          properties:
            firstName:
              type: string
              description: Имя студента
              example: "Алиш"
            lastName:
              type: string
              description: Фамилия студента
              example: "Рахмонов"
            email:
              type: string
              description: Email адрес
              example: "a.rahmonov@student.ttpu.uz"
            phone:
              type: string
              description: Номер телефона в формате +998XXXXXXXXX
              example: "+998901234567"
            studentId:
              type: string
              description: Студенческий ID (8 цифр)
              example: "12345678"
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
            degreeLevel:
              type: string
              enum: [bachelor, master, phd, dsc]
              description: Уровень образования
              example: "bachelor"
            studentType:
              type: string
              enum: [regular, free_applicant, external]
              description: Тип студента (обязательно для PhD/DSc)
              example: "regular"
            admissionYear:
              type: integer
              description: Год поступления
              example: 2021
            graduationYear:
              type: integer
              description: Год выпуска
              example: 2025
            financingType:
              type: string
              enum: [budget, contract]
              description: Тип финансирования
              example: "budget"
    responses:
      201:
        description: Студент успешно создан
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
            message:
              type: string
              example: "Student created successfully"
      400:
        description: Ошибка валидации данных
      403:
        description: Доступ запрещен (только для администраторов)
      409:
        description: Студент с таким email или ID уже существует
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
    
    # Student ID validation
    if not validate_student_id(data['studentId']):
        errors.append({'field': 'studentId', 'message': 'Student ID must be 8 digits'})
    
    # Password validation
    is_valid_password, password_error = validate_password(data['password'])
    if not is_valid_password:
        errors.append({'field': 'password', 'message': password_error})
    
    # Degree level validation
    if data['degreeLevel'] not in ['bachelor', 'master', 'phd', 'dsc']:
        errors.append({'field': 'degreeLevel', 'message': 'Invalid degree level'})
    
    # Student type validation
    student_type = data.get('studentType', 'regular')
    if data['degreeLevel'] in ['bachelor', 'master'] and student_type != 'regular':
        errors.append({'field': 'studentType', 'message': 'Bachelor and Master students must be regular type'})
    elif data['degreeLevel'] in ['phd', 'dsc'] and student_type not in ['regular', 'free_applicant', 'external']:
        errors.append({'field': 'studentType', 'message': 'Invalid student type for PhD/DSc'})
    
    # Check for existing users
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        errors.append({'field': 'email', 'message': 'Email already registered'})
    
    if 'phone' in data and data['phone']:
        existing_phone = User.query.filter_by(phone=data['phone']).first()
        if existing_phone:
            errors.append({'field': 'phone', 'message': 'Phone number already registered'})
    
    existing_student = User.query.filter_by(student_id=data['studentId']).first()
    if existing_student:
        errors.append({'field': 'studentId', 'message': 'Student ID already registered'})
    
    if errors:
        return error_response('VALIDATION_ERROR', 'Validation failed', errors, 422)
    
    # Create new student
    student = User(
        first_name=data['firstName'],
        last_name=data['lastName'],
        middle_name=data.get('middleName'),
        email=data['email'],
        phone=data.get('phone'),
        student_id=data['studentId'],
        role='student',
        faculty=data.get('faculty'),
        direction=data.get('direction'),
        degree_level=data['degreeLevel'],
        student_type=student_type,
        admission_year=data.get('admissionYear'),
        graduation_year=data.get('graduationYear'),
        financing_type=data.get('financingType'),
        is_verified=True,  # Admin-created students are auto-verified
        email_verified=True
    )
    student.set_password(data['password'])
    
    db.session.add(student)
    db.session.commit()
    
    # Log activity
    activity_log = ActivityLog(
        user_id=current_user.id,
        action='STUDENT_CREATED',
        target_id=student.id,
        target_type='user',
        details=f'Created student {student.email} with degree level {student.degree_level}',
        ip_address=request.environ.get('REMOTE_ADDR'),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(activity_log)
    db.session.commit()
    
    return success_response(student.to_dict(), status_code=201)

@admin_bp.route('/students/<student_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
@validate_json_data()
def update_admin_student(current_user, data, student_id):
    """Update student information (Admin only)
    ---
    tags:
      - Admin - Students
    summary: Обновить информацию о студенте (для администраторов)
    description: Обновляет информацию о студенте
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        type: string
        required: true
        description: ID студента
      - in: body
        name: student_data
        description: Данные для обновления студента
        required: true
        schema:
          type: object
          properties:
            firstName:
              type: string
              description: Имя студента
            lastName:
              type: string
              description: Фамилия студента
            email:
              type: string
              description: Email адрес
            phone:
              type: string
              description: Номер телефона
            studentId:
              type: string
              description: Студенческий ID
            faculty:
              type: string
              description: Факультет
            direction:
              type: string
              description: Направление обучения
            degreeLevel:
              type: string
              enum: [bachelor, master, phd, dsc]
              description: Уровень образования
            studentType:
              type: string
              enum: [regular, free_applicant, external]
              description: Тип студента
            admissionYear:
              type: integer
              description: Год поступления
            graduationYear:
              type: integer
              description: Год выпуска
            financingType:
              type: string
              enum: [budget, contract]
              description: Тип финансирования
    responses:
      200:
        description: Информация о студенте успешно обновлена
      400:
        description: Ошибка валидации данных
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Студент не найден
    """
    student = User.query.filter_by(id=student_id, role='student').first()
    if not student:
        return error_response('STUDENT_NOT_FOUND', 'Student not found', status_code=404)
    
    # Validate input data
    errors = []
    
    # Email validation (if being updated)
    if 'email' in data and data['email'] != student.email:
        if not validate_email_format(data['email']):
            errors.append({'field': 'email', 'message': 'Invalid email format'})
        
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            errors.append({'field': 'email', 'message': 'Email already registered'})
    
    # Phone validation (if being updated)
    if 'phone' in data and data['phone'] and data['phone'] != student.phone:
        if not validate_phone_format(data['phone']):
            errors.append({'field': 'phone', 'message': 'Invalid phone format'})
        
        existing_phone = User.query.filter_by(phone=data['phone']).first()
        if existing_phone:
            errors.append({'field': 'phone', 'message': 'Phone number already registered'})
    
    # Student ID validation (if being updated)
    if 'studentId' in data and data['studentId'] and data['studentId'] != student.student_id:
        if not validate_student_id(data['studentId']):
            errors.append({'field': 'studentId', 'message': 'Student ID must be 8 digits'})
        
        existing_student = User.query.filter_by(student_id=data['studentId']).first()
        if existing_student:
            errors.append({'field': 'studentId', 'message': 'Student ID already registered'})
    
    # Degree level validation (if being updated)
    if 'degreeLevel' in data and data['degreeLevel'] not in ['bachelor', 'master', 'phd', 'dsc']:
        errors.append({'field': 'degreeLevel', 'message': 'Invalid degree level'})
    
    if errors:
        return error_response('VALIDATION_ERROR', 'Validation failed', errors, 422)
    
    # Update student fields
    updatable_fields = [
        'firstName', 'lastName', 'middleName', 'email', 'phone', 'studentId',
        'faculty', 'direction', 'degreeLevel', 'studentType', 'admissionYear', 
        'graduationYear', 'financingType'
    ]
    
    field_map = {
        'firstName': 'first_name',
        'lastName': 'last_name',
        'middleName': 'middle_name',
        'studentId': 'student_id',
        'degreeLevel': 'degree_level',
        'studentType': 'student_type',
        'admissionYear': 'admission_year',
        'graduationYear': 'graduation_year',
        'financingType': 'financing_type'
    }
    
    updated_fields = []
    for field in updatable_fields:
        if field in data:
            db_field = field_map.get(field, field)
            if hasattr(student, db_field):
                old_value = getattr(student, db_field)
                new_value = data[field]
                if old_value != new_value:
                    setattr(student, db_field, new_value)
                    updated_fields.append(field)
    
    if updated_fields:
        student.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log activity
        activity_log = ActivityLog(
            user_id=current_user.id,
            action='STUDENT_UPDATED',
            target_id=student.id,
            target_type='user',
            details=f'Updated student fields: {", ".join(updated_fields)}',
            ip_address=request.environ.get('REMOTE_ADDR'),
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(activity_log)
        db.session.commit()
    
    return success_response(student.to_dict())

@admin_bp.route('/students/<student_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_admin_student(current_user, student_id):
    """Delete a student (Admin only)
    ---
    tags:
      - Admin - Students
    summary: Удалить студента (для администраторов)
    description: Удаляет студента из системы
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        type: string
        required: true
        description: ID студента для удаления
    responses:
      200:
        description: Студент успешно удален
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Student deleted successfully"
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Студент не найден
    """
    student = User.query.filter_by(id=student_id, role='student').first()
    if not student:
        return error_response('STUDENT_NOT_FOUND', 'Student not found', status_code=404)
    
    student_email = student.email
    db.session.delete(student)
    db.session.commit()
    
    # Log activity
    activity_log = ActivityLog(
        user_id=current_user.id,
        action='STUDENT_DELETED',
        target_id=student_id,
        target_type='user',
        details=f'Deleted student {student_email}',
        ip_address=request.environ.get('REMOTE_ADDR'),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(activity_log)
    db.session.commit()
    
    return success_response(message='Student deleted successfully')

@admin_bp.route('/students/<student_id>/verify', methods=['PATCH'])
@jwt_required()
@role_required('admin')
def verify_admin_student(current_user, student_id):
    """Verify a student account (Admin only)
    ---
    tags:
      - Admin - Students
    summary: Верифицировать аккаунт студента (для администраторов)
    description: Административная верификация аккаунта студента
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        type: string
        required: true
        description: ID студента для верификации
    responses:
      200:
        description: Студент успешно верифицирован
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
            message:
              type: string
              example: "Student verified successfully"
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Студент не найден
      400:
        description: Студент уже верифицирован
    """
    student = User.query.filter_by(id=student_id, role='student').first()
    if not student:
        return error_response('STUDENT_NOT_FOUND', 'Student not found', status_code=404)
    
    if student.is_verified:
        return error_response('ALREADY_VERIFIED', 'Student is already verified', status_code=400)
    
    student.is_verified = True
    student.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Create notification for student
    notification = Notification(
        user_id=student.id,
        title='Аккаунт верифицирован',
        message='Ваш студенческий аккаунт был верифицирован администратором. Теперь вы можете использовать все функции системы.',
        type='success'
    )
    db.session.add(notification)
    
    # Log activity
    activity_log = ActivityLog(
        user_id=current_user.id,
        action='STUDENT_VERIFIED',
        target_id=student.id,
        target_type='user',
        details=f'Verified student {student.email}',
        ip_address=request.environ.get('REMOTE_ADDR'),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(activity_log)
    db.session.commit()
    
    return success_response(student.to_dict(), message='Student verified successfully')

@admin_bp.route('/students/<student_id>/block', methods=['PATCH'])
@jwt_required()
@role_required('admin')
@validate_json_data(required_fields=['blocked'])
def block_admin_student(current_user, data, student_id):
    """Block or unblock a student (Admin only)
    ---
    tags:
      - Admin - Students
    summary: Заблокировать или разблокировать студента (для администраторов)
    description: Административная блокировка или разблокировка аккаунта студента
    security:
      - Bearer: []
    parameters:
      - in: path
        name: student_id
        type: string
        required: true
        description: ID студента
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
        description: Статус блокировки студента успешно изменен
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
            message:
              type: string
              example: "Student blocked successfully"
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Студент не найден
    """
    student = User.query.filter_by(id=student_id, role='student').first()
    if not student:
        return error_response('STUDENT_NOT_FOUND', 'Student not found', status_code=404)
    
    blocked = data['blocked']
    reason = data.get('reason', '') if blocked else None
    
    student.is_blocked = blocked
    student.block_reason = reason
    student.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Create notification for student
    if blocked:
        notification = Notification(
            user_id=student.id,
            title='Аккаунт заблокирован',
            message=f'Ваш студенческий аккаунт был заблокирован. Причина: {reason}',
            type='error'
        )
    else:
        notification = Notification(
            user_id=student.id,
            title='Аккаунт разблокирован',
            message='Ваш студенческий аккаунт был разблокирован. Вы можете снова использовать систему.',
            type='success'
        )
    
    db.session.add(notification)
    
    # Log activity
    action = 'STUDENT_BLOCKED' if blocked else 'STUDENT_UNBLOCKED'
    details = f'{"Blocked" if blocked else "Unblocked"} student {student.email}'
    if blocked and reason:
        details += f' with reason: {reason}'
    
    activity_log = ActivityLog(
        user_id=current_user.id,
        action=action,
        target_id=student.id,
        target_type='user',
        details=details,
        ip_address=request.environ.get('REMOTE_ADDR'),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(activity_log)
    db.session.commit()
    
    action_text = 'blocked' if blocked else 'unblocked'
    return success_response(student.to_dict(), message=f'Student {action_text} successfully')

# ========== TEACHER CRUD ENDPOINTS ==========

@admin_bp.route('/teachers', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_admin_teachers(current_user):
    """Get list of all teachers with filtering (Admin only)
    ---
    tags:
      - Admin - Teachers
    summary: Получить список всех преподавателей (для администраторов)
    description: Возвращает пагинированный список всех преподавателей с возможностью фильтрации
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
        description: Поиск по имени, фамилии или email
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
        description: Список преподавателей успешно получен
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
                      faculty:
                        type: string
                      direction:
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
    
    # Base query for teachers only
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
    
    verified = request.args.get('verified')
    if verified is not None:
        query = query.filter(User.is_verified == (verified.lower() == 'true'))
    
    # Sort by creation date (newest first)
    query = query.order_by(User.created_at.desc())
    
    return success_response(create_pagination_response(query, page, limit))

@admin_bp.route('/teachers/<teacher_id>', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_admin_teacher(current_user, teacher_id):
    """Get detailed information about a teacher (Admin only)
    ---
    tags:
      - Admin - Teachers
    summary: Получить детальную информацию о преподавателе (для администраторов)
    description: Возвращает подробную информацию о преподавателе по ID
    security:
      - Bearer: []
    parameters:
      - in: path
        name: teacher_id
        type: string
        required: true
        description: ID преподавателя
    responses:
      200:
        description: Информация о преподавателе успешно получена
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
                faculty:
                  type: string
                direction:
                  type: string
                isVerified:
                  type: boolean
                isBlocked:
                  type: boolean
                createdAt:
                  type: string
                  format: date-time
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Преподаватель не найден
    """
    teacher = User.query.filter_by(id=teacher_id, role='teacher').first()
    if not teacher:
        return error_response('TEACHER_NOT_FOUND', 'Teacher not found', status_code=404)
    
    return success_response(teacher.to_dict())

@admin_bp.route('/teachers', methods=['POST'])
@jwt_required()
@role_required('admin')
@validate_json_data(required_fields=[
    'firstName', 'lastName', 'email', 'password'
])
def create_admin_teacher(current_user, data):
    """Create a new teacher (Admin only)
    ---
    tags:
      - Admin - Teachers
    summary: Создать нового преподавателя (для администраторов)
    description: Создает нового преподавателя в системе
    security:
      - Bearer: []
    parameters:
      - in: body
        name: teacher_data
        description: Данные нового преподавателя
        required: true
        schema:
          type: object
          required:
            - firstName
            - lastName
            - email
            - password
          properties:
            firstName:
              type: string
              description: Имя преподавателя
              example: "Дилшод"
            lastName:
              type: string
              description: Фамилия преподавателя
              example: "Каримов"
            email:
              type: string
              description: Email адрес
              example: "d.karimov@ttpu.uz"
            phone:
              type: string
              description: Номер телефона в формате +998XXXXXXXXX
              example: "+998901234567"
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
              description: Направление/кафедра
              example: "Computer Science"
    responses:
      201:
        description: Преподаватель успешно создан
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
            message:
              type: string
              example: "Teacher created successfully"
      400:
        description: Ошибка валидации данных
      403:
        description: Доступ запрещен (только для администраторов)
      409:
        description: Преподаватель с таким email уже существует
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
    
    if errors:
        return error_response('VALIDATION_ERROR', 'Validation failed', errors, 422)
    
    # Create new teacher
    teacher = User(
        first_name=data['firstName'],
        last_name=data['lastName'],
        middle_name=data.get('middleName'),
        email=data['email'],
        phone=data.get('phone'),
        role='teacher',
        faculty=data.get('faculty'),
        direction=data.get('direction'),
        is_verified=True,  # Admin-created teachers are auto-verified
        email_verified=True
    )
    teacher.set_password(data['password'])
    
    db.session.add(teacher)
    db.session.commit()
    
    # Log activity
    activity_log = ActivityLog(
        user_id=current_user.id,
        action='TEACHER_CREATED',
        target_id=teacher.id,
        target_type='user',
        details=f'Created teacher {teacher.email}',
        ip_address=request.environ.get('REMOTE_ADDR'),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(activity_log)
    db.session.commit()
    
    return success_response(teacher.to_dict(), status_code=201)

@admin_bp.route('/teachers/<teacher_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
@validate_json_data()
def update_admin_teacher(current_user, data, teacher_id):
    """Update teacher information (Admin only)
    ---
    tags:
      - Admin - Teachers
    summary: Обновить информацию о преподавателе (для администраторов)
    description: Обновляет информацию о преподавателе
    security:
      - Bearer: []
    parameters:
      - in: path
        name: teacher_id
        type: string
        required: true
        description: ID преподавателя
      - in: body
        name: teacher_data
        description: Данные для обновления преподавателя
        required: true
        schema:
          type: object
          properties:
            firstName:
              type: string
              description: Имя преподавателя
            lastName:
              type: string
              description: Фамилия преподавателя
            email:
              type: string
              description: Email адрес
            phone:
              type: string
              description: Номер телефона
            faculty:
              type: string
              description: Факультет
            direction:
              type: string
              description: Направление/кафедра
    responses:
      200:
        description: Информация о преподавателе успешно обновлена
      400:
        description: Ошибка валидации данных
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Преподаватель не найден
    """
    teacher = User.query.filter_by(id=teacher_id, role='teacher').first()
    if not teacher:
        return error_response('TEACHER_NOT_FOUND', 'Teacher not found', status_code=404)
    
    # Validate input data
    errors = []
    
    # Email validation (if being updated)
    if 'email' in data and data['email'] != teacher.email:
        if not validate_email_format(data['email']):
            errors.append({'field': 'email', 'message': 'Invalid email format'})
        
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            errors.append({'field': 'email', 'message': 'Email already registered'})
    
    # Phone validation (if being updated)
    if 'phone' in data and data['phone'] and data['phone'] != teacher.phone:
        if not validate_phone_format(data['phone']):
            errors.append({'field': 'phone', 'message': 'Invalid phone format'})
        
        existing_phone = User.query.filter_by(phone=data['phone']).first()
        if existing_phone:
            errors.append({'field': 'phone', 'message': 'Phone number already registered'})
    
    if errors:
        return error_response('VALIDATION_ERROR', 'Validation failed', errors, 422)
    
    # Update teacher fields
    updatable_fields = [
        'firstName', 'lastName', 'middleName', 'email', 'phone', 
        'faculty', 'direction'
    ]
    
    field_map = {
        'firstName': 'first_name',
        'lastName': 'last_name',
        'middleName': 'middle_name'
    }
    
    updated_fields = []
    for field in updatable_fields:
        if field in data:
            db_field = field_map.get(field, field)
            if hasattr(teacher, db_field):
                old_value = getattr(teacher, db_field)
                new_value = data[field]
                if old_value != new_value:
                    setattr(teacher, db_field, new_value)
                    updated_fields.append(field)
    
    if updated_fields:
        teacher.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Log activity
        activity_log = ActivityLog(
            user_id=current_user.id,
            action='TEACHER_UPDATED',
            target_id=teacher.id,
            target_type='user',
            details=f'Updated teacher fields: {", ".join(updated_fields)}',
            ip_address=request.environ.get('REMOTE_ADDR'),
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(activity_log)
        db.session.commit()
    
    return success_response(teacher.to_dict())

@admin_bp.route('/teachers/<teacher_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_admin_teacher(current_user, teacher_id):
    """Delete a teacher (Admin only)
    ---
    tags:
      - Admin - Teachers
    summary: Удалить преподавателя (для администраторов)
    description: Удаляет преподавателя из системы
    security:
      - Bearer: []
    parameters:
      - in: path
        name: teacher_id
        type: string
        required: true
        description: ID преподавателя для удаления
    responses:
      200:
        description: Преподаватель успешно удален
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Teacher deleted successfully"
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Преподаватель не найден
    """
    teacher = User.query.filter_by(id=teacher_id, role='teacher').first()
    if not teacher:
        return error_response('TEACHER_NOT_FOUND', 'Teacher not found', status_code=404)
    
    teacher_email = teacher.email
    db.session.delete(teacher)
    db.session.commit()
    
    # Log activity
    activity_log = ActivityLog(
        user_id=current_user.id,
        action='TEACHER_DELETED',
        target_id=teacher_id,
        target_type='user',
        details=f'Deleted teacher {teacher_email}',
        ip_address=request.environ.get('REMOTE_ADDR'),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(activity_log)
    db.session.commit()
    
    return success_response(message='Teacher deleted successfully')

@admin_bp.route('/teachers/<teacher_id>/verify', methods=['PATCH'])
@jwt_required()
@role_required('admin')
def verify_admin_teacher(current_user, teacher_id):
    """Verify a teacher account (Admin only)
    ---
    tags:
      - Admin - Teachers
    summary: Верифицировать аккаунт преподавателя (для администраторов)
    description: Административная верификация аккаунта преподавателя
    security:
      - Bearer: []
    parameters:
      - in: path
        name: teacher_id
        type: string
        required: true
        description: ID преподавателя для верификации
    responses:
      200:
        description: Преподаватель успешно верифицирован
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
            message:
              type: string
              example: "Teacher verified successfully"
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Преподаватель не найден
      400:
        description: Преподаватель уже верифицирован
    """
    teacher = User.query.filter_by(id=teacher_id, role='teacher').first()
    if not teacher:
        return error_response('TEACHER_NOT_FOUND', 'Teacher not found', status_code=404)
    
    if teacher.is_verified:
        return error_response('ALREADY_VERIFIED', 'Teacher is already verified', status_code=400)
    
    teacher.is_verified = True
    teacher.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Create notification for teacher
    notification = Notification(
        user_id=teacher.id,
        title='Аккаунт верифицирован',
        message='Ваш преподавательский аккаунт был верифицирован администратором. Теперь вы можете использовать все функции системы.',
        type='success'
    )
    db.session.add(notification)
    
    # Log activity
    activity_log = ActivityLog(
        user_id=current_user.id,
        action='TEACHER_VERIFIED',
        target_id=teacher.id,
        target_type='user',
        details=f'Verified teacher {teacher.email}',
        ip_address=request.environ.get('REMOTE_ADDR'),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(activity_log)
    db.session.commit()
    
    return success_response(teacher.to_dict(), message='Teacher verified successfully')

@admin_bp.route('/teachers/<teacher_id>/block', methods=['PATCH'])
@jwt_required()
@role_required('admin')
@validate_json_data(required_fields=['blocked'])
def block_admin_teacher(current_user, data, teacher_id):
    """Block or unblock a teacher (Admin only)
    ---
    tags:
      - Admin - Teachers
    summary: Заблокировать или разблокировать преподавателя (для администраторов)
    description: Административная блокировка или разблокировка аккаунта преподавателя
    security:
      - Bearer: []
    parameters:
      - in: path
        name: teacher_id
        type: string
        required: true
        description: ID преподавателя
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
        description: Статус блокировки преподавателя успешно изменен
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
            message:
              type: string
              example: "Teacher blocked successfully"
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Преподаватель не найден
    """
    teacher = User.query.filter_by(id=teacher_id, role='teacher').first()
    if not teacher:
        return error_response('TEACHER_NOT_FOUND', 'Teacher not found', status_code=404)
    
    blocked = data['blocked']
    reason = data.get('reason', '') if blocked else None
    
    teacher.is_blocked = blocked
    teacher.block_reason = reason
    teacher.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Create notification for teacher
    if blocked:
        notification = Notification(
            user_id=teacher.id,
            title='Аккаунт заблокирован',
            message=f'Ваш преподавательский аккаунт был заблокирован. Причина: {reason}',
            type='error'
        )
    else:
        notification = Notification(
            user_id=teacher.id,
            title='Аккаунт разблокирован',
            message='Ваш преподавательский аккаунт был разблокирован. Вы можете снова использовать систему.',
            type='success'
        )
    
    db.session.add(notification)
    
    # Log activity
    action = 'TEACHER_BLOCKED' if blocked else 'TEACHER_UNBLOCKED'
    details = f'{"Blocked" if blocked else "Unblocked"} teacher {teacher.email}'
    if blocked and reason:
        details += f' with reason: {reason}'
    
    activity_log = ActivityLog(
        user_id=current_user.id,
        action=action,
        target_id=teacher.id,
        target_type='user',
        details=details,
        ip_address=request.environ.get('REMOTE_ADDR'),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(activity_log)
    db.session.commit()
    
    action_text = 'blocked' if blocked else 'unblocked'
    return success_response(teacher.to_dict(), message=f'Teacher {action_text} successfully')

# ========== TEACHER-STUDENT ASSIGNMENT ENDPOINTS ==========

@admin_bp.route('/teachers/<teacher_id>/students', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_teacher_students(current_user, teacher_id):
    """Get students assigned to a teacher (Admin only)
    ---
    tags:
      - Admin - Teacher Assignments
    summary: Получить студентов, прикрепленных к преподавателю (для администраторов)
    description: Возвращает список студентов, прикрепленных к конкретному преподавателю
    security:
      - Bearer: []
    parameters:
      - in: path
        name: teacher_id
        type: string
        required: true
        description: ID преподавателя
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
    responses:
      200:
        description: Список студентов успешно получен
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                teacher:
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
                      studentId:
                        type: string
                      faculty:
                        type: string
                      direction:
                        type: string
                      degreeLevel:
                        type: string
                      assignedAt:
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
      404:
        description: Преподаватель не найден
    """
    teacher = User.query.filter_by(id=teacher_id, role='teacher').first()
    if not teacher:
        return error_response('TEACHER_NOT_FOUND', 'Teacher not found', status_code=404)
    
    page, limit = get_pagination_params()
    
    # Query teacher-student assignments
    from app.database import TeacherStudent
    query = db.session.query(User, TeacherStudent).join(
        TeacherStudent, User.id == TeacherStudent.student_id
    ).filter(TeacherStudent.teacher_id == teacher_id)
    
    # Apply pagination
    from sqlalchemy import func
    total = query.count()
    total_pages = (total + limit - 1) // limit
    
    items = query.offset((page - 1) * limit).limit(limit).all()
    
    # Format response
    students = []
    for student, assignment in items:
        student_data = student.to_dict()
        student_data['assignedAt'] = assignment.assigned_at.isoformat() if assignment.assigned_at else None
        students.append(student_data)
    
    return success_response({
        'teacher': {
            'id': teacher.id,
            'firstName': teacher.first_name,
            'lastName': teacher.last_name,
            'email': teacher.email,
            'faculty': teacher.faculty,
            'direction': teacher.direction
        },
        'items': students,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'totalPages': total_pages
        }
    })

@admin_bp.route('/teachers/<teacher_id>/students', methods=['POST'])
@jwt_required()
@role_required('admin')
@validate_json_data(required_fields=['studentIds'])
def assign_students_to_teacher(current_user, data, teacher_id):
    """Assign students to a teacher (Admin only)
    ---
    tags:
      - Admin - Teacher Assignments
    summary: Назначить студентов преподавателю (для администраторов)
    description: Назначает одного или нескольких студентов конкретному преподавателю
    security:
      - Bearer: []
    parameters:
      - in: path
        name: teacher_id
        type: string
        required: true
        description: ID преподавателя
      - in: body
        name: assignment_data
        description: Данные для назначения студентов
        required: true
        schema:
          type: object
          required:
            - studentIds
          properties:
            studentIds:
              type: array
              items:
                type: string
              description: Массив ID студентов для назначения
              example: ["student1", "student2", "student3"]
    responses:
      200:
        description: Студенты успешно назначены преподавателю
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                assigned:
                  type: integer
                  description: Количество назначенных студентов
                skipped:
                  type: integer
                  description: Количество пропущенных (уже назначенных) студентов
                errors:
                  type: array
                  description: Ошибки при назначении
            message:
              type: string
              example: "Students assigned successfully"
      400:
        description: Ошибка валидации данных
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Преподаватель не найден
    """
    teacher = User.query.filter_by(id=teacher_id, role='teacher').first()
    if not teacher:
        return error_response('TEACHER_NOT_FOUND', 'Teacher not found', status_code=404)
    
    student_ids = data['studentIds']
    if not isinstance(student_ids, list) or not student_ids:
        return error_response('INVALID_STUDENT_IDS', 'Student IDs must be a non-empty array', status_code=400)
    
    from app.database import TeacherStudent
    assigned_count = 0
    skipped_count = 0
    errors = []
    
    for student_id in student_ids:
        # Check if student exists
        student = User.query.filter_by(id=student_id, role='student').first()
        if not student:
            errors.append(f'Student {student_id} not found')
            continue
        
        # Check if assignment already exists
        existing_assignment = TeacherStudent.query.filter_by(
            teacher_id=teacher_id, 
            student_id=student_id
        ).first()
        
        if existing_assignment:
            skipped_count += 1
            continue
        
        # Create new assignment
        assignment = TeacherStudent(
            teacher_id=teacher_id,
            student_id=student_id,
            assigned_by=current_user.id
        )
        db.session.add(assignment)
        assigned_count += 1
    
    if assigned_count > 0:
        db.session.commit()
        
        # Log activity
        activity_log = ActivityLog(
            user_id=current_user.id,
            action='STUDENTS_ASSIGNED_TO_TEACHER',
            target_id=teacher_id,
            target_type='user',
            details=f'Assigned {assigned_count} students to teacher {teacher.email}',
            ip_address=request.environ.get('REMOTE_ADDR'),
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(activity_log)
        db.session.commit()
    
    return success_response({
        'assigned': assigned_count,
        'skipped': skipped_count,
        'errors': errors
    }, message=f'Assignment completed: {assigned_count} assigned, {skipped_count} skipped')

@admin_bp.route('/teachers/<teacher_id>/students/<student_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def unassign_student_from_teacher(current_user, teacher_id, student_id):
    """Remove student assignment from teacher (Admin only)
    ---
    tags:
      - Admin - Teacher Assignments
    summary: Удалить назначение студента у преподавателя (для администраторов)
    description: Убирает назначение конкретного студента у преподавателя
    security:
      - Bearer: []
    parameters:
      - in: path
        name: teacher_id
        type: string
        required: true
        description: ID преподавателя
      - in: path
        name: student_id
        type: string
        required: true
        description: ID студента
    responses:
      200:
        description: Назначение успешно удалено
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Student unassigned from teacher successfully"
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Назначение не найдено
    """
    from app.database import TeacherStudent
    assignment = TeacherStudent.query.filter_by(
        teacher_id=teacher_id, 
        student_id=student_id
    ).first()
    
    if not assignment:
        return error_response('ASSIGNMENT_NOT_FOUND', 'Assignment not found', status_code=404)
    
    # Get teacher and student info for logging
    teacher = User.query.get(teacher_id)
    student = User.query.get(student_id)
    
    db.session.delete(assignment)
    db.session.commit()
    
    # Log activity
    activity_log = ActivityLog(
        user_id=current_user.id,
        action='STUDENT_UNASSIGNED_FROM_TEACHER',
        target_id=teacher_id,
        target_type='user',
        details=f'Unassigned student {student.email if student else student_id} from teacher {teacher.email if teacher else teacher_id}',
        ip_address=request.environ.get('REMOTE_ADDR'),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(activity_log)
    db.session.commit()
    
    return success_response(message='Student unassigned from teacher successfully')
