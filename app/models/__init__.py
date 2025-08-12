from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import secrets
import string

# We'll inject db in the create_app function
db = None

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: secrets.token_urlsafe(16))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, index=True)
    student_id = db.Column(db.String(20), unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'teacher', 'student', name='user_roles'), default='student')
    
    # Student specific fields
    faculty = db.Column(db.String(100))
    direction = db.Column(db.String(100))
    admission_year = db.Column(db.Integer)
    graduation_year = db.Column(db.Integer)
    financing_type = db.Column(db.Enum('budget', 'contract', name='financing_types'))
    
    # Status fields
    is_verified = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    block_reason = db.Column(db.Text)
    email_verified = db.Column(db.Boolean, default=False)
    phone_verified = db.Column(db.Boolean, default=False)
    
    # File fields
    avatar_url = db.Column(db.String(500))
    cv_url = db.Column(db.String(500))
    diploma_url = db.Column(db.String(500))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Verification tokens
    email_verification_token = db.Column(db.String(100))
    password_reset_token = db.Column(db.String(100))
    password_reset_expires = db.Column(db.DateTime)
    
    # Relationships
    work_experiences = db.relationship('WorkExperience', backref='user', lazy=True, cascade='all, delete-orphan')
    education_goals = db.relationship('EducationGoal', backref='user', lazy=True, cascade='all, delete-orphan')
    created_activity_logs = db.relationship('ActivityLog', foreign_keys='ActivityLog.user_id', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_verification_token(self):
        self.email_verification_token = secrets.token_urlsafe(32)
        return self.email_verification_token
    
    def generate_password_reset_token(self):
        self.password_reset_token = secrets.token_urlsafe(32)
        self.password_reset_expires = datetime.utcnow() + timedelta(hours=24)
        return self.password_reset_token
    
    def to_dict(self):
        return {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'middleName': self.middle_name,
            'email': self.email,
            'phone': self.phone,
            'studentId': self.student_id,
            'role': self.role,
            'faculty': self.faculty,
            'direction': self.direction,
            'admissionYear': self.admission_year,
            'graduationYear': self.graduation_year,
            'financingType': self.financing_type,
            'isVerified': self.is_verified,
            'isBlocked': self.is_blocked,
            'blockReason': self.block_reason,
            'emailVerified': self.email_verified,
            'phoneVerified': self.phone_verified,
            'avatar': self.avatar_url,
            'cvUrl': self.cv_url,
            'diplomaUrl': self.diploma_url,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'lastLogin': self.last_login.isoformat() if self.last_login else None
        }

class WorkExperience(db.Model):
    __tablename__ = 'work_experiences'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: secrets.token_urlsafe(16))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    position = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'company': self.company,
            'position': self.position,
            'startDate': self.start_date.isoformat() if self.start_date else None,
            'endDate': self.end_date.isoformat() if self.end_date else None,
            'description': self.description,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

class EducationGoal(db.Model):
    __tablename__ = 'education_goals'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: secrets.token_urlsafe(16))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    goal = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'year': self.year,
            'goal': self.goal,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

class TeacherStudent(db.Model):
    __tablename__ = 'teacher_students'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: secrets.token_urlsafe(16))
    teacher_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Relationships
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='assigned_students')
    student = db.relationship('User', foreign_keys=[student_id], backref='assigned_teachers')
    assigner = db.relationship('User', foreign_keys=[assigned_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'teacherId': self.teacher_id,
            'studentId': self.student_id,
            'assignedAt': self.assigned_at.isoformat() if self.assigned_at else None,
            'assignedBy': self.assigned_by
        }

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: secrets.token_urlsafe(16))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    target_id = db.Column(db.String(36))
    target_type = db.Column(db.String(50))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'action': self.action,
            'targetId': self.target_id,
            'targetType': self.target_type,
            'details': self.details,
            'ipAddress': self.ip_address,
            'userAgent': self.user_agent,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: secrets.token_urlsafe(16))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.Enum('info', 'warning', 'success', 'error', name='notification_types'), default='info')
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'read': self.read,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'readAt': self.read_at.isoformat() if self.read_at else None
        }

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: secrets.token_urlsafe(16))
    name = db.Column(db.String(200), nullable=False, unique=True)
    website = db.Column(db.String(500))
    industry = db.Column(db.String(100))
    location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'website': self.website,
            'industry': self.industry,
            'location': self.location,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

class Faculty(db.Model):
    __tablename__ = 'faculties'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: secrets.token_urlsafe(16))
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    directions = db.relationship('Direction', backref='faculty', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

class Direction(db.Model):
    __tablename__ = 'directions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: secrets.token_urlsafe(16))
    faculty_id = db.Column(db.String(36), db.ForeignKey('faculties.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'facultyId': self.faculty_id,
            'name': self.name,
            'description': self.description,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: secrets.token_urlsafe(16))
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.Enum('student_progress', 'faculty_statistics', 'employment_report', name='report_types'), nullable=False)
    parameters = db.Column(db.JSON)
    file_path = db.Column(db.String(500))
    status = db.Column(db.Enum('pending', 'processing', 'completed', 'failed', name='report_status'), default='pending')
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    creator = db.relationship('User', backref='created_reports')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'parameters': self.parameters,
            'filePath': self.file_path,
            'status': self.status,
            'createdBy': self.created_by,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'completedAt': self.completed_at.isoformat() if self.completed_at else None
        }