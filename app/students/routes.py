from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.database import db, User, TeacherStudent
from app.utils.decorators import (
    role_required, success_response, error_response,
    get_pagination_params, create_pagination_response
)

students_bp = Blueprint('students', __name__)

@students_bp.route('', methods=['GET'])
@jwt_required()
def get_students(current_user=None):
    """Get list of students
    ---
    tags:
      - Students
    summary: Получить список студентов
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
                        example: "Алиш"
                      lastName:
                        type: string
                        example: "Рахмонов"
                      email:
                        type: string
                        example: "a.rahmonov@student.ttpu.uz"
                      studentId:
                        type: string
                        example: "20230001"
                      faculty:
                        type: string
                        example: "Engineering"
                      direction:
                        type: string
                        example: "Computer Science"
                      year:
                        type: integer
                        example: 3
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
      401:
        description: Не авторизован
    """
    # This will be properly implemented with role checks
    page, limit = get_pagination_params()
    
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
    
    query = query.order_by(User.created_at.desc())
    
    return success_response(create_pagination_response(query, page, limit))