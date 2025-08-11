from flask import Blueprint
from app.utils.decorators import success_response

users_bp = Blueprint('users', __name__)

# Placeholder routes - will be implemented based on priority
@users_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check"""
    return success_response({'status': 'healthy'})