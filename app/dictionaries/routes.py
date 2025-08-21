from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.database import db, Faculty, Direction, Company
from app.utils.decorators import (
    success_response, error_response, validate_json_data,
    get_pagination_params, create_pagination_response, role_required
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
      - Bearer: []
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
      - Bearer: []
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
      - Bearer: []
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

# ========== FACULTY CRUD ENDPOINTS ==========

@dictionaries_bp.route('/faculties', methods=['POST'])
@jwt_required()
@role_required('admin')
@validate_json_data(required_fields=['name'])
def create_faculty(current_user, data):
    """Create a new faculty (Admin only)
    ---
    tags:
      - Dictionaries
    summary: Создать новый факультет (для администраторов)
    description: Создает новый факультет в системе
    security:
      - Bearer: []
    parameters:
      - in: body
        name: faculty_data
        description: Данные нового факультета
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              description: Название факультета
              example: "Факультет информационных технологий"
            description:
              type: string
              description: Описание факультета
              example: "Факультет подготовки специалистов в области IT"
    responses:
      201:
        description: Факультет успешно создан
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
                description:
                  type: string
                createdAt:
                  type: string
                  format: date-time
      400:
        description: Факультет с таким названием уже существует или ошибка валидации
      401:
        description: Не авторизован
      403:
        description: Доступ запрещен (только для администраторов)
    """
    # Check if faculty already exists
    existing_faculty = Faculty.query.filter_by(name=data['name']).first()
    if existing_faculty:
        return error_response('FACULTY_EXISTS', 'Faculty with this name already exists', status_code=400)
    
    faculty = Faculty(
        name=data['name'],
        description=data.get('description')
    )
    
    db.session.add(faculty)
    db.session.commit()
    
    return success_response(faculty.to_dict(), status_code=201)

@dictionaries_bp.route('/faculties/<faculty_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
@validate_json_data()
def update_faculty(current_user, data, faculty_id):
    """Update a faculty (Admin only)
    ---
    tags:
      - Dictionaries
    summary: Обновить факультет (для администраторов)
    description: Обновляет данные существующего факультета
    security:
      - Bearer: []
    parameters:
      - in: path
        name: faculty_id
        type: string
        required: true
        description: ID факультета
      - in: body
        name: faculty_data
        description: Новые данные факультета
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              description: Название факультета
              example: "Новое название факультета"
            description:
              type: string
              description: Описание факультета
              example: "Обновленное описание факультета"
    responses:
      200:
        description: Факультет успешно обновлен
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
                description:
                  type: string
                createdAt:
                  type: string
                  format: date-time
      400:
        description: Факультет с таким названием уже существует или ошибка валидации
      401:
        description: Не авторизован
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Факультет не найден
    """
    faculty = Faculty.query.get(faculty_id)
    if not faculty:
        return error_response('FACULTY_NOT_FOUND', 'Faculty not found', status_code=404)
    
    # Check if new name already exists (if name is being changed)
    if 'name' in data and data['name'] != faculty.name:
        existing_faculty = Faculty.query.filter_by(name=data['name']).first()
        if existing_faculty:
            return error_response('FACULTY_EXISTS', 'Faculty with this name already exists', status_code=400)
        faculty.name = data['name']
    
    # Update description if provided
    if 'description' in data:
        faculty.description = data['description']
    
    db.session.commit()
    
    return success_response(faculty.to_dict())

@dictionaries_bp.route('/faculties/<faculty_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_faculty(current_user, faculty_id):
    """Delete a faculty (Admin only)
    ---
    tags:
      - Dictionaries
    summary: Удалить факультет (для администраторов)
    description: Удаляет факультет из системы. Внимание! Это также удалит все направления, связанные с этим факультетом.
    security:
      - Bearer: []
    parameters:
      - in: path
        name: faculty_id
        type: string
        required: true
        description: ID факультета
    responses:
      200:
        description: Факультет успешно удален
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Faculty deleted successfully"
      401:
        description: Не авторизован
      403:
        description: Доступ запрещен (только для администраторов)
      404:
        description: Факультет не найден
    """
    faculty = Faculty.query.get(faculty_id)
    if not faculty:
        return error_response('FACULTY_NOT_FOUND', 'Faculty not found', status_code=404)
    
    # The cascade='all, delete-orphan' in the Faculty model will automatically delete related directions
    db.session.delete(faculty)
    db.session.commit()
    
    return success_response({'message': 'Faculty deleted successfully'})