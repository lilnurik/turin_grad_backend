from flask import Blueprint, jsonify
from app.utils.decorators import success_response

system_bp = Blueprint('system', __name__)

@system_bp.route('/health', methods=['GET'])
def health():
    """System health check
    ---
    tags:
      - System
    summary: Проверка здоровья системы
    description: Проверяет состояние API и возвращает статус работоспособности
    responses:
      200:
        description: Система работает нормально
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                status:
                  type: string
                  example: "healthy"
                service:
                  type: string
                  example: "Turin Grad Hub API"
                version:
                  type: string
                  example: "1.0.0"
    """
    return success_response({
        'status': 'healthy',
        'service': 'Turin Grad Hub API',
        'version': '1.0.0'
    })

@system_bp.route('/info', methods=['GET'])
def info():
    """API information
    ---
    tags:
      - System
    summary: Информация об API
    description: Возвращает базовую информацию о API, включая версию и количество endpoints
    responses:
      200:
        description: Информация об API
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                name:
                  type: string
                  example: "Turin Grad Hub API"
                version:
                  type: string
                  example: "1.0.0"
                description:
                  type: string
                  example: "Backend API for Turin Grad Hub - Graduate Management System"
                endpoints:
                  type: integer
                  example: 87
    """
    return success_response({
        'name': 'Turin Grad Hub API',
        'version': '1.0.0',
        'description': 'Backend API for Turin Grad Hub - Graduate Management System',
        'endpoints': 87
    })

@system_bp.route('/config', methods=['GET'])
def config():
    """Client configuration
    ---
    tags:
      - System
    summary: Конфигурация клиента
    description: Возвращает конфигурационные параметры для клиентского приложения
    responses:
      200:
        description: Конфигурация клиента
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                maxFileSize:
                  type: string
                  example: "16MB"
                supportedImageFormats:
                  type: array
                  items:
                    type: string
                  example: ["jpg", "jpeg", "png"]
                supportedDocumentFormats:
                  type: array
                  items:
                    type: string
                  example: ["pdf", "doc", "docx"]
                features:
                  type: object
                  properties:
                    emailVerification:
                      type: boolean
                      example: true
                    smsVerification:
                      type: boolean
                      example: true
                    adminApproval:
                      type: boolean
                      example: true
                    fileUploads:
                      type: boolean
                      example: true
    """
    return success_response({
        'maxFileSize': '16MB',
        'supportedImageFormats': ['jpg', 'jpeg', 'png'],
        'supportedDocumentFormats': ['pdf', 'doc', 'docx'],
        'features': {
            'emailVerification': True,
            'smsVerification': True,
            'adminApproval': True,
            'fileUploads': True
        }
    })