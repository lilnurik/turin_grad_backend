from flask import Blueprint, jsonify
from app.utils.decorators import success_response

system_bp = Blueprint('system', __name__)

@system_bp.route('/health', methods=['GET'])
def health():
    """System health check"""
    return success_response({
        'status': 'healthy',
        'service': 'Turin Grad Hub API',
        'version': '1.0.0'
    })

@system_bp.route('/info', methods=['GET'])
def info():
    """API information"""
    return success_response({
        'name': 'Turin Grad Hub API',
        'version': '1.0.0',
        'description': 'Backend API for Turin Grad Hub - Graduate Management System',
        'endpoints': 87
    })

@system_bp.route('/config', methods=['GET'])
def config():
    """Client configuration"""
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