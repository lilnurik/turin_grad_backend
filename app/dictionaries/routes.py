from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.database import db, Faculty, Direction, Company
from app.utils.decorators import (
    success_response, error_response, validate_json_data,
    get_pagination_params, create_pagination_response
)

dictionaries_bp = Blueprint('dictionaries', __name__)

@dictionaries_bp.route('/faculties', methods=['GET'])
@jwt_required()
def get_faculties():
    """Get list of faculties
    ---
    tags:
      - Dictionaries
    summary: Получить список факультетов
    description: Возвращает список всех факультетов университета
    security:
      - UserAuth: []
    responses:
      200:
        description: Список факультетов успешно получен
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
                  name:
                    type: string
                    example: "Engineering"
                  nameRu:
                    type: string
                    example: "Инженерный факультет"
                  nameUz:
                    type: string
                    example: "Muhandislik fakulteti"
                  code:
                    type: string
                    example: "ENG"
                  description:
                    type: string
                    example: "Faculty of Engineering and Technology"
      401:
        description: Не авторизован
    """
    faculties = Faculty.query.order_by(Faculty.name).all()
    return success_response([faculty.to_dict() for faculty in faculties])

@dictionaries_bp.route('/directions', methods=['GET'])
@jwt_required()
def get_directions():
    """Get list of directions
    ---
    tags:
      - Dictionaries
    summary: Получить список направлений
    description: Возвращает список направлений обучения, опционально отфильтрованный по факультету
    security:
      - UserAuth: []
    parameters:
      - in: query
        name: facultyId
        type: string
        description: ID факультета для фильтрации направлений
    responses:
      200:
        description: Список направлений успешно получен
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
                  name:
                    type: string
                    example: "Computer Science"
                  nameRu:
                    type: string
                    example: "Информатика и вычислительная техника"
                  nameUz:
                    type: string
                    example: "Informatika va hisoblash texnikasi"
                  code:
                    type: string
                    example: "CS"
                  facultyId:
                    type: string
                  faculty:
                    type: object
                    properties:
                      name:
                        type: string
                      code:
                        type: string
      401:
        description: Не авторизован
    """
    query = Direction.query
    
    # Filter by faculty if provided
    faculty_id = request.args.get('facultyId')
    if faculty_id:
        query = query.filter_by(faculty_id=faculty_id)
    
    directions = query.order_by(Direction.name).all()
    return success_response([direction.to_dict() for direction in directions])

@dictionaries_bp.route('/companies', methods=['GET'])
@jwt_required()
def get_companies():
    """Get list of companies
    ---
    tags:
      - Dictionaries
    summary: Получить список компаний
    description: Возвращает пагинированный список компаний с возможностью поиска
    security:
      - UserAuth: []
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
        description: Поиск по названию компании
    responses:
      200:
        description: Список компаний успешно получен
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
                      name:
                        type: string
                        example: "ООО 'Технологии'"
                      website:
                        type: string
                        example: "https://example.com"
                      industry:
                        type: string
                        example: "IT"
                      location:
                        type: string
                        example: "Ташкент, Узбекистан"
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
    
    query = Company.query
    
    # Apply search filter
    search = request.args.get('search')
    if search:
        search_filter = f"%{search}%"
        query = query.filter(Company.name.ilike(search_filter))
    
    # Sort by name
    query = query.order_by(Company.name)
    
    return success_response(create_pagination_response(query, page, limit))

@dictionaries_bp.route('/companies', methods=['POST'])
@jwt_required()
@validate_json_data(required_fields=['name'])
def add_company(data):
    """Add a new company
    ---
    tags:
      - Dictionaries
    summary: Добавить новую компанию
    description: Добавляет новую компанию в базу данных
    security:
      - UserAuth: []
    parameters:
      - in: body
        name: company_data
        description: Данные новой компании
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              description: Название компании
              example: "ООО 'Новые технологии'"
            website:
              type: string
              description: Веб-сайт компании
              example: "https://newtech.uz"
            industry:
              type: string
              description: Отрасль деятельности
              example: "IT"
            location:
              type: string
              description: Местоположение
              example: "Ташкент, Узбекистан"
    responses:
      201:
        description: Компания успешно добавлена
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
                name:
                  type: string
                website:
                  type: string
                industry:
                  type: string
                location:
                  type: string
                createdAt:
                  type: string
                  format: date-time
      400:
        description: Компания с таким названием уже существует или ошибка валидации
      401:
        description: Не авторизован
    """
    # Check if company already exists
    existing_company = Company.query.filter_by(name=data['name']).first()
    if existing_company:
        return error_response('COMPANY_EXISTS', 'Company already exists', status_code=400)
    
    company = Company(
        name=data['name'],
        website=data.get('website'),
        industry=data.get('industry'),
        location=data.get('location')
    )
    
    db.session.add(company)
    db.session.commit()
    
    return success_response(company.to_dict(), status_code=201)