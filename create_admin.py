#!/usr/bin/env python3
"""
Script to create an admin user for the Turin Grad Hub system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from app.database import db, User
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_admin_user():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///turin_grad.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@ttpu.uz').first()
        if admin:
            print("Admin user already exists!")
            return
        
        # Create admin user
        admin = User(
            first_name="System",
            last_name="Administrator",
            email="admin@ttpu.uz",
            role="admin",
            is_verified=True,
            email_verified=True
        )
        admin.set_password("admin123")
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"Admin user created successfully!")
        print(f"Email: admin@ttpu.uz")
        print(f"Password: admin123")
        print(f"User ID: {admin.id}")

if __name__ == "__main__":
    create_admin_user()