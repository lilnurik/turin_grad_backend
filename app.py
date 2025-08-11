from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flasgger import Swagger
from datetime import timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database and models
from app.database import db

# Initialize other extensions
jwt = JWTManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///turin_grad.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Mail Configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    
    # File Upload Configuration
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app)
    
    # Swagger Configuration
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs/"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Turin Grad Hub API",
            "description": "Backend API для системы управления выпускниками Turin Grad Hub - Туринский политехнический университет Ташкента (TTPU)",
            "contact": {
                "responsibleOrganization": "TTPU",
                "responsibleDeveloper": "Turin Grad Hub Team"
            },
            "version": "1.0.0"
        },
        "host": "127.0.0.1:5000",
        "basePath": "/",
        "schemes": ["http", "https"],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ]
    }
    
    swagger = Swagger(app, config=swagger_config, template=swagger_template)
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.users.routes import users_bp
    from app.students.routes import students_bp
    from app.teachers.routes import teachers_bp
    from app.profile.routes import profile_bp
    from app.admin.routes import admin_bp
    from app.system.routes import system_bp
    from app.notifications.routes import notifications_bp
    from app.dictionaries.routes import dictionaries_bp
    from app.search.routes import search_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api')
    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(teachers_bp, url_prefix='/api/teachers')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(system_bp, url_prefix='/api')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(dictionaries_bp, url_prefix='/api/dictionaries')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    
    # ReDoc endpoint
    @app.route('/api/redoc/')
    def redoc():
        """
        ReDoc documentation endpoint
        ---
        tags:
          - Documentation
        responses:
          200:
            description: ReDoc documentation interface
        """
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Turin Grad Hub API - ReDoc</title>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { 
                    margin: 0; 
                    padding: 0; 
                    font-family: Arial, sans-serif;
                }
                #redoc-container { 
                    min-height: 100vh; 
                }
                .loading {
                    text-align: center;
                    padding: 50px;
                    font-size: 18px;
                    color: #666;
                }
            </style>
        </head>
        <body>
            <div id="redoc-container">
                <div class="loading">
                    <h2>Turin Grad Hub API - ReDoc Documentation</h2>
                    <p>Loading API documentation...</p>
                    <p>If this doesn't load automatically, you can access the OpenAPI spec directly: 
                       <a href="/apispec_1.json">JSON specification</a>
                    </p>
                    <p>Or use the <a href="/api/docs/">Swagger UI interface</a></p>
                </div>
            </div>
            <script>
                // Fallback to show spec link if ReDoc fails to load
                setTimeout(function() {
                    if (!window.Redoc) {
                        document.getElementById('redoc-container').innerHTML = 
                            '<div class="loading">' +
                            '<h2>Turin Grad Hub API Documentation</h2>' +
                            '<p>ReDoc interface is not available in this environment.</p>' +
                            '<p>Please use:</p>' +
                            '<ul style="text-align: left; display: inline-block;">' +
                            '<li><a href="/api/docs/">Swagger UI interface</a> - Interactive documentation</li>' +
                            '<li><a href="/apispec_1.json">OpenAPI JSON specification</a> - Raw API spec</li>' +
                            '</ul>' +
                            '</div>';
                    }
                }, 3000);
            </script>
            <script src="https://unpkg.com/redoc@2.0.0/bundles/redoc.standalone.js"></script>
            <script>
                if (window.Redoc) {
                    Redoc.init('/apispec_1.json', {
                        theme: {
                            colors: {
                                primary: {
                                    main: '#1976d2'
                                }
                            },
                            typography: {
                                fontSize: '14px',
                                fontFamily: 'Arial, sans-serif'
                            }
                        }
                    }, document.getElementById('redoc-container'));
                }
            </script>
        </body>
        </html>
        '''
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'BAD_REQUEST',
                'message': 'Bad request'
            }
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'UNAUTHORIZED',
                'message': 'Unauthorized access'
            }
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'FORBIDDEN',
                'message': 'Access forbidden'
            }
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Resource not found'
            }
        }), 404
    
    @app.errorhandler(422)
    def validation_error(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Validation failed'
            }
        }), 422
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Internal server error'
            }
        }), 500
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)