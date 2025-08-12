from flask_mail import Message
from flask import current_app
import secrets
import random
import string

def send_email(to, subject, template, **kwargs):
    """Send email with template"""
    try:
        from app import mail
        msg = Message(
            subject=subject,
            recipients=[to],
            html=template,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False

def send_verification_email(user):
    """Send email verification"""
    token = user.generate_verification_token()
    subject = "Подтвердите ваш email - Turin Grad Hub"
    
    verification_link = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/verify-email?token={token}"
    
    template = f"""
    <h2>Добро пожаловать в Turin Grad Hub!</h2>
    <p>Здравствуйте, {user.first_name}!</p>
    <p>Для завершения регистрации, пожалуйста, подтвердите ваш email, нажав на ссылку ниже:</p>
    <p><a href="{verification_link}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Подтвердить email</a></p>
    <p>Если вы не регистрировались в нашей системе, просто проигнорируйте это письмо.</p>
    <p>С уважением,<br>Команда Turin Grad Hub</p>
    """
    
    return send_email(user.email, subject, template)

def send_password_reset_email(user):
    """Send password reset email"""
    token = user.generate_password_reset_token()
    subject = "Сброс пароля - Turin Grad Hub"
    
    reset_link = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={token}"
    
    template = f"""
    <h2>Сброс пароля</h2>
    <p>Здравствуйте, {user.first_name}!</p>
    <p>Вы запросили сброс пароля для вашего аккаунта в Turin Grad Hub.</p>
    <p>Для создания нового пароля, нажмите на ссылку ниже:</p>
    <p><a href="{reset_link}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Сбросить пароль</a></p>
    <p>Эта ссылка действительна в течение 24 часов.</p>
    <p>Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.</p>
    <p>С уважением,<br>Команда Turin Grad Hub</p>
    """
    
    return send_email(user.email, subject, template)

def send_admin_verification_request(user):
    """Send notification to admins about new user verification request"""
    from app.database import User
    
    admins = User.query.filter_by(role='admin', is_blocked=False).all()
    subject = "Новый запрос на верификацию пользователя - Turin Grad Hub"
    
    admin_panel_link = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/admin/users/{user.id}"
    
    template = f"""
    <h2>Новый запрос на верификацию</h2>
    <p>Пользователь запросил верификацию аккаунта:</p>
    <ul>
        <li><strong>Имя:</strong> {user.first_name} {user.last_name}</li>
        <li><strong>Email:</strong> {user.email}</li>
        <li><strong>Телефон:</strong> {user.phone or 'Не указан'}</li>
        <li><strong>Студенческий ID:</strong> {user.student_id or 'Не указан'}</li>
        <li><strong>Факультет:</strong> {user.faculty or 'Не указан'}</li>
        <li><strong>Направление:</strong> {user.direction or 'Не указано'}</li>
        <li><strong>Роль:</strong> {user.role}</li>
    </ul>
    <p><a href="{admin_panel_link}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Перейти к верификации</a></p>
    <p>С уважением,<br>Система Turin Grad Hub</p>
    """
    
    for admin in admins:
        send_email(admin.email, subject, template)

def generate_sms_code():
    """Generate 6-digit SMS verification code"""
    return ''.join(random.choices(string.digits, k=6))

def send_sms_code(phone, code):
    """Send SMS verification code (mock implementation)"""
    # This is a mock implementation
    # In production, integrate with SMS provider like Twilio, SMS.uz, etc.
    current_app.logger.info(f"SMS code {code} sent to {phone}")
    return True

# Mock SMS storage for development
sms_codes = {}

def store_sms_code(phone, code):
    """Store SMS code temporarily (for development)"""
    sms_codes[phone] = code

def verify_sms_code(phone, code):
    """Verify SMS code (for development)"""
    stored_code = sms_codes.get(phone)
    if stored_code == code:
        sms_codes.pop(phone, None)  # Remove used code
        return True
    return False