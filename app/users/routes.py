from flask import Blueprint
from app.utils.decorators import success_response

users_bp = Blueprint('users', __name__)

# Placeholder routes - will be implemented based on priority
@users_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check
    ---
    tags:
      - Users
    summary: Проверка здоровья модуля пользователей
    description: Базовая проверка работоспособности модуля пользователей
    responses:
      200:
        description: Модуль работает нормально
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
    """
    return success_response({'status': 'healthy'})