from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.database import db, User, Company
from app.utils.decorators import (
    success_response, get_pagination_params, create_pagination_response
)

search_bp = Blueprint('search', __name__)

@search_bp.route('', methods=['GET'])
@jwt_required()
def global_search():
    """Global search across the system
    ---
    tags:
      - Search
    summary: Глобальный поиск по системе
    description: Выполняет поиск по пользователям и компаниям в зависимости от указанного типа
    security:
      - Bearer: []
    parameters:
      - in: query
        name: q
        type: string
        required: true
        description: Поисковый запрос
      - in: query
        name: type
        type: string
        enum: [all, users, companies]
        default: all
        description: Тип поиска
      - in: query
        name: page
        type: integer
        description: Номер страницы для пагинации (только при конкретном типе)
        default: 1
      - in: query
        name: limit
        type: integer
        description: Количество элементов на странице (только при конкретном типе)
        default: 10
    responses:
      200:
        description: Результаты поиска
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                users:
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
                companies:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: string
                      name:
                        type: string
                      website:
                        type: string
                      industry:
                        type: string
                pagination:
                  type: object
                  description: Пагинация (только при поиске конкретного типа)
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
    q = request.args.get('q', '').strip()
    if not q:
        return success_response({'users': [], 'companies': []})
    
    search_type = request.args.get('type', 'all')
    page, limit = get_pagination_params()
    
    results = {}
    search_filter = f"%{q}%"
    
    if search_type in ['all', 'users']:
        # Search users
        user_query = User.query.filter(
            db.or_(
                User.first_name.ilike(search_filter),
                User.last_name.ilike(search_filter),
                User.email.ilike(search_filter),
                User.student_id.ilike(search_filter)
            )
        ).order_by(User.created_at.desc())
        
        if search_type == 'users':
            results = create_pagination_response(user_query, page, limit)
        else:
            results['users'] = [user.to_dict() for user in user_query.limit(10).all()]
    
    if search_type in ['all', 'companies']:
        # Search companies
        company_query = Company.query.filter(
            Company.name.ilike(search_filter)
        ).order_by(Company.name)
        
        if search_type == 'companies':
            results = create_pagination_response(company_query, page, limit)
        else:
            results['companies'] = [company.to_dict() for company in company_query.limit(10).all()]
    
    return success_response(results)

@search_bp.route('/students', methods=['GET'])
@jwt_required()
def search_students():
    """Search students with advanced filters
    ---
    tags:
      - Search
    summary: Расширенный поиск студентов
    description: Выполняет поиск студентов с возможностью применения различных фильтров
    security:
      - Bearer: []
    parameters:
      - in: query
        name: q
        type: string
        description: Поисковый запрос по имени, фамилии, email или студенческому ID
      - in: query
        name: faculty
        type: string
        description: Фильтр по факультету
      - in: query
        name: direction
        type: string
        description: Фильтр по направлению обучения
      - in: query
        name: admissionYear
        type: integer
        description: Фильтр по году поступления
      - in: query
        name: graduationYear
        type: integer
        description: Фильтр по году выпуска
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
        description: Результаты поиска студентов
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
                      admissionYear:
                        type: integer
                        example: 2020
                      graduationYear:
                        type: integer
                        example: 2024
                      year:
                        type: integer
                        example: 3
                      isVerified:
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
      401:
        description: Не авторизован
    """
    page, limit = get_pagination_params()
    
    # Base query for students
    query = User.query.filter_by(role='student')
    
    # Apply filters
    q = request.args.get('q')
    if q:
        search_filter = f"%{q}%"
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
    
    direction = request.args.get('direction')
    if direction:
        query = query.filter(User.direction == direction)
    
    admission_year = request.args.get('admissionYear', type=int)
    if admission_year:
        query = query.filter(User.admission_year == admission_year)
    
    graduation_year = request.args.get('graduationYear', type=int)
    if graduation_year:
        query = query.filter(User.graduation_year == graduation_year)
    
    # Sort by name
    query = query.order_by(User.first_name, User.last_name)
    
    return success_response(create_pagination_response(query, page, limit))