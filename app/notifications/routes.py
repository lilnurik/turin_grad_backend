from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db, Notification
from app.utils.decorators import (
    success_response, error_response, get_pagination_params, create_pagination_response
)
from datetime import datetime

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get user notifications
    ---
    tags:
      - Notifications
    summary: Получить уведомления пользователя
    description: Возвращает пагинированный список уведомлений текущего пользователя
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
        name: read
        type: boolean
        description: Фильтр по статусу прочтения
      - in: query
        name: type
        type: string
        description: Фильтр по типу уведомления
        enum: [VERIFICATION_REQUEST, ACCOUNT_VERIFIED, ACCOUNT_BLOCKED, PASSWORD_RESET, SYSTEM_UPDATE, WELCOME, ACHIEVEMENT]
    responses:
      200:
        description: Уведомления успешно получены
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
                      type:
                        type: string
                        example: "ACCOUNT_VERIFIED"
                      title:
                        type: string
                        example: "Аккаунт верифицирован"
                      message:
                        type: string
                        example: "Ваш аккаунт успешно верифицирован администратором"
                      read:
                        type: boolean
                        example: false
                      readAt:
                        type: string
                        format: date-time
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
    current_user_id = get_jwt_identity()
    page, limit = get_pagination_params()
    
    # Base query
    query = Notification.query.filter_by(user_id=current_user_id)
    
    # Apply filters
    read_filter = request.args.get('read')
    if read_filter is not None:
        query = query.filter(Notification.read == (read_filter.lower() == 'true'))
    
    notification_type = request.args.get('type')
    if notification_type:
        query = query.filter(Notification.type == notification_type)
    
    # Sort by creation date (newest first)
    query = query.order_by(Notification.created_at.desc())
    
    return success_response(create_pagination_response(query, page, limit))

@notifications_bp.route('/<notification_id>/read', methods=['PATCH'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark notification as read
    ---
    tags:
      - Notifications
    summary: Отметить уведомление как прочитанное
    description: Помечает указанное уведомление пользователя как прочитанное
    security:
      - Bearer: []
    parameters:
      - in: path
        name: notification_id
        type: string
        required: true
        description: ID уведомления
    responses:
      200:
        description: Уведомление успешно отмечено как прочитанное
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
                type:
                  type: string
                title:
                  type: string
                message:
                  type: string
                read:
                  type: boolean
                  example: true
                readAt:
                  type: string
                  format: date-time
                createdAt:
                  type: string
                  format: date-time
      401:
        description: Не авторизован
      404:
        description: Уведомление не найдено
    """
    current_user_id = get_jwt_identity()
    
    notification = Notification.query.filter_by(
        id=notification_id, 
        user_id=current_user_id
    ).first()
    
    if not notification:
        return error_response('NOTIFICATION_NOT_FOUND', 'Notification not found', status_code=404)
    
    if not notification.read:
        notification.read = True
        notification.read_at = datetime.utcnow()
        db.session.commit()
    
    return success_response(notification.to_dict())

@notifications_bp.route('/mark-all-read', methods=['PATCH'])
@jwt_required()
def mark_all_notifications_read():
    """Mark all notifications as read
    ---
    tags:
      - Notifications
    summary: Отметить все уведомления как прочитанные
    description: Помечает все непрочитанные уведомления пользователя как прочитанные
    security:
      - Bearer: []
    responses:
      200:
        description: Все уведомления успешно отмечены как прочитанные
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Marked 5 notifications as read"
      401:
        description: Не авторизован
    """
    current_user_id = get_jwt_identity()
    
    unread_notifications = Notification.query.filter_by(
        user_id=current_user_id,
        read=False
    ).all()
    
    for notification in unread_notifications:
        notification.read = True
        notification.read_at = datetime.utcnow()
    
    db.session.commit()
    
    return success_response(message=f'Marked {len(unread_notifications)} notifications as read')