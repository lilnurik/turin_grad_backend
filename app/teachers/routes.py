from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.database import db, User
from app.utils.decorators import (
    success_response, get_pagination_params, create_pagination_response
)

teachers_bp = Blueprint('teachers', __name__)

@teachers_bp.route('', methods=['GET'])
@jwt_required()
def get_teachers():
    """Get list of teachers
    ---
    tags:
      - Teachers
    summary: Получить список преподавателей
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
                        example: "Дилшод"
                      lastName:
                        type: string
                        example: "Каримов"
                      email:
                        type: string
                        example: "d.karimov@ttpu.uz"
                      faculty:
                        type: string
                        example: "Engineering"
                      department:
                        type: string
                        example: "Computer Science"
                      position:
                        type: string
                        example: "Senior Lecturer"
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
    page, limit = get_pagination_params()
    
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
    
    query = query.order_by(User.created_at.desc())
    
    return success_response(create_pagination_response(query, page, limit))