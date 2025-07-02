from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import json

from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_active_user
# from app.services.notification_service import notification_service  # Uncomment when service is implemented

router = APIRouter()

# Connection manager for WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except:
                # Connection closed, remove it
                self.disconnect(user_id)

    async def broadcast(self, message: str):
        disconnected_users = []
        for user_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except:
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            self.disconnect(user_id)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for real-time notifications"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive and listen for messages
            data = await websocket.receive_text()
            # Echo received message (can be enhanced with actual logic)
            await manager.send_personal_message(f"Message received: {data}", user_id)
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@router.get("/", response_model=List[Dict[str, Any]])
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False, description="Show only unread notifications"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's notifications"""
    try:
        # This is a placeholder implementation
        # In a real app, you would fetch from a notifications table
        sample_notifications = [
            {
                "id": 1,
                "title": "New question available",
                "message": "A new question in Mathematics has been added",
                "type": "question_added",
                "is_read": False,
                "created_at": datetime.utcnow().isoformat(),
                "data": {"subject_id": 1, "question_id": 123}
            },
            {
                "id": 2,
                "title": "Practice session completed",
                "message": "You completed a practice session with 85% accuracy",
                "type": "session_completed",
                "is_read": True,
                "created_at": datetime.utcnow().isoformat(),
                "data": {"session_id": 456, "accuracy": 85}
            }
        ]
        
        if unread_only:
            sample_notifications = [n for n in sample_notifications if not n["is_read"]]
        
        return sample_notifications[skip:skip+limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/unread-count", response_model=Dict[str, int])
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get count of unread notifications"""
    try:
        # Placeholder implementation
        return {"unread_count": 3}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a notification as read"""
    try:
        # Placeholder implementation
        return {"message": f"Notification {notification_id} marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark all notifications as read"""
    try:
        # Placeholder implementation
        return {"message": "All notifications marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a notification"""
    try:
        # Placeholder implementation
        return {"message": f"Notification {notification_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/settings", response_model=Dict[str, Any])
async def update_notification_settings(
    settings: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user's notification preferences"""
    try:
        # Placeholder implementation
        # In a real app, you would save these settings to the database
        return {
            "message": "Notification settings updated",
            "settings": settings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/settings", response_model=Dict[str, Any])
async def get_notification_settings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's notification preferences"""
    try:
        # Placeholder implementation
        return {
            "email_notifications": True,
            "push_notifications": True,
            "practice_reminders": True,
            "achievement_notifications": True,
            "new_question_alerts": False,
            "daily_digest": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send", response_model=Dict[str, Any])
async def send_notification(
    user_id: int,
    title: str,
    message: str,
    notification_type: str = "general",
    data: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Send a real-time notification to a specific user (admin only)"""
    try:
        # Check if user has admin privileges
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Create notification payload
        notification = {
            "id": f"notif_{datetime.utcnow().timestamp()}",
            "title": title,
            "message": message,
            "type": notification_type,
            "data": data or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Send real-time notification via WebSocket
        await manager.send_personal_message(json.dumps(notification), user_id)
        
        return {
            "message": "Notification sent successfully",
            "notification_id": notification["id"],
            "recipient": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/broadcast", response_model=Dict[str, Any])
async def broadcast_notification(
    title: str,
    message: str,
    notification_type: str = "announcement",
    data: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Broadcast a notification to all connected users (admin only)"""
    try:
        # Check if user has admin privileges
        if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Create notification payload
        notification = {
            "id": f"broadcast_{datetime.utcnow().timestamp()}",
            "title": title,
            "message": message,
            "type": notification_type,
            "data": data or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Broadcast to all connected users
        await manager.broadcast(json.dumps(notification))
        
        return {
            "message": "Notification broadcasted successfully",
            "notification_id": notification["id"],
            "connected_users": len(manager.active_connections)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=Dict[str, Any])
async def get_notification_status():
    """Get notification system status"""
    return {
        "system_status": "active",
        "connected_users": len(manager.active_connections),
        "websocket_connections": list(manager.active_connections.keys())
    } 