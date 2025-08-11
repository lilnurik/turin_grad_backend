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
    """Get user notifications"""
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
    """Mark notification as read"""
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
    """Mark all notifications as read"""
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