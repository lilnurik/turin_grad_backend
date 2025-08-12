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
    """Get current user profile
    ---
    tags:
      - Profile
    summary: Получить профиль текущего пользователя
    description: Возвращает информацию о профиле авторизованного пользователя
    security:
      - Bearer: []
    responses:
      200:
        description: Профиль пользователя
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
                  example: "user_id"
                firstName:
                  type: string
                  example: "Алишер"
                lastName:
                  type: string
                  example: "Рахмонов"
                middleName:
                  type: string
                  example: "Абдуллаевич"
                email:
                  type: string
                  example: "a.rahmonov@student.ttpu.uz"
                phone:
                  type: string
                  example: "+998901234567"
                role:
                  type: string
                  enum: ["admin", "teacher", "student"]
                  example: "student"
                faculty:
                  type: string
                  example: "Информационные технологии"
                direction:
                  type: string
                  example: "Программная инженерия"
                studentId:
                  type: string
                  example: "12345678"
                isVerified:
                  type: boolean
                  example: true
                isApproved:
                  type: boolean
                  example: true
                avatar:
                  type: string
                  example: "avatar_url"
                createdAt:
                  type: string
                  format: date-time
                  example: "2025-01-15T08:00:00Z"
                lastLogin:
                  type: string
                  format: date-time
                  example: "2025-01-15T08:00:00Z"
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
      404:
        description: Пользователь не найден
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
                  example: "User not found"
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return error_response('USER_NOT_FOUND', 'User not found', status_code=404)
    
    return success_response(user.to_dict())

@profile_bp.route('', methods=['PUT'])
@jwt_required()
@validate_json_data()
def update_profile(data):
    """Update current user profile
    ---
    tags:
      - Profile
    summary: Обновить профиль пользователя
    description: Обновляет разрешенные поля профиля авторизованного пользователя
    security:
      - Bearer: []
    parameters:
      - in: body
        name: profile_data
        description: Данные для обновления профиля
        required: true
        schema:
          type: object
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
              description: Отчество пользователя
              example: "Абдуллаевич"
            phone:
              type: string
              description: Номер телефона
              example: "+998901234567"
            faculty:
              type: string
              description: Факультет
              example: "Информационные технологии"
            direction:
              type: string
              description: Направление обучения
              example: "Программная инженерия"
    responses:
      200:
        description: Профиль успешно обновлен
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              description: Обновленные данные профиля
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
      404:
        description: Пользователь не найден
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
                  example: "User not found"
    """
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
    """Get user work experience
    ---
    tags:
      - Profile
    summary: Получить опыт работы пользователя
    description: Возвращает список всего опыта работы текущего пользователя
    security:
      - Bearer: []
    responses:
      200:
        description: Опыт работы успешно получен
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  company:
                    type: string
                    example: "ООО 'Технологии'"
                  position:
                    type: string
                    example: "Разработчик"
                  startDate:
                    type: string
                    format: date
                    example: "2022-01-15"
                  endDate:
                    type: string
                    format: date
                    example: "2023-06-30"
                  description:
                    type: string
                    example: "Разработка веб-приложений на Python"
                  createdAt:
                    type: string
                    format: date-time
      401:
        description: Не авторизован
    """
    current_user_id = get_jwt_identity()
    experiences = WorkExperience.query.filter_by(user_id=current_user_id).all()
    
    return success_response([exp.to_dict() for exp in experiences])

@profile_bp.route('/work-experience', methods=['POST'])
@jwt_required()
@validate_json_data(required_fields=['company', 'position', 'startDate'])
def add_work_experience(data):
    """Add work experience
    ---
    tags:
      - Profile
    summary: Добавить опыт работы
    description: Добавляет новый опыт работы для текущего пользователя
    security:
      - Bearer: []
    parameters:
      - in: body
        name: experience_data
        description: Данные опыта работы
        required: true
        schema:
          type: object
          required:
            - company
            - position
            - startDate
          properties:
            company:
              type: string
              description: Название компании
              example: "ООО 'Технологии'"
            position:
              type: string
              description: Должность
              example: "Разработчик"
            startDate:
              type: string
              format: date
              description: Дата начала работы
              example: "2022-01-15"
            endDate:
              type: string
              format: date
              description: Дата окончания работы (если работа завершена)
              example: "2023-06-30"
            description:
              type: string
              description: Описание обязанностей и достижений
              example: "Разработка веб-приложений на Python и JavaScript"
    responses:
      201:
        description: Опыт работы успешно добавлен
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
                company:
                  type: string
                position:
                  type: string
                startDate:
                  type: string
                  format: date
                endDate:
                  type: string
                  format: date
                description:
                  type: string
                createdAt:
                  type: string
                  format: date-time
            message:
              type: string
              example: "Work experience added successfully"
      400:
        description: Ошибка валидации данных
      401:
        description: Не авторизован
    """
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
    """Get user education goals
    ---
    tags:
      - Profile
    summary: Получить образовательные цели пользователя
    description: Возвращает список всех образовательных целей текущего пользователя
    security:
      - Bearer: []
    responses:
      200:
        description: Образовательные цели успешно получены
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  year:
                    type: integer
                    example: 2024
                  goal:
                    type: string
                    example: "Изучить машинное обучение"
                  description:
                    type: string
                    example: "Освоить основы ML и применить их в проектах"
                  completed:
                    type: boolean
                    example: false
                  createdAt:
                    type: string
                    format: date-time
      401:
        description: Не авторизован
    """
    current_user_id = get_jwt_identity()
    goals = EducationGoal.query.filter_by(user_id=current_user_id).all()
    
    return success_response([goal.to_dict() for goal in goals])

@profile_bp.route('/education-goals', methods=['POST'])
@jwt_required()
@validate_json_data(required_fields=['year', 'goal'])
def add_education_goal(data):
    """Add education goal
    ---
    tags:
      - Profile
    summary: Добавить образовательную цель
    description: Добавляет новую образовательную цель для текущего пользователя
    security:
      - Bearer: []
    parameters:
      - in: body
        name: goal_data
        description: Данные образовательной цели
        required: true
        schema:
          type: object
          required:
            - year
            - goal
          properties:
            year:
              type: integer
              description: Год достижения цели
              example: 2024
            goal:
              type: string
              description: Описание цели
              example: "Изучить машинное обучение"
            description:
              type: string
              description: Подробное описание цели
              example: "Освоить основы ML, пройти курсы и применить знания в проектах"
    responses:
      201:
        description: Образовательная цель успешно добавлена
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
                year:
                  type: integer
                goal:
                  type: string
                description:
                  type: string
                completed:
                  type: boolean
                  example: false
                createdAt:
                  type: string
                  format: date-time
            message:
              type: string
              example: "Education goal added successfully"
      400:
        description: Ошибка валидации данных
      401:
        description: Не авторизован
    """
    current_user_id = get_jwt_identity()
    
    goal = EducationGoal(
        user_id=current_user_id,
        year=data['year'],
        goal=data['goal']
    )
    
    db.session.add(goal)
    db.session.commit()
    
    return success_response(goal.to_dict(), status_code=201)