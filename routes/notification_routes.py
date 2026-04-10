from fastapi import APIRouter, Depends, HTTPException
from db.database import SessionLocal
from modules.notification import Notification
from utils.security import get_current_user

router = APIRouter()



@router.get("/notifications")
def get_notifications(current_user=Depends(get_current_user)):
    db = SessionLocal()

    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.id.desc()).all()

    db.close()

    return notifications



@router.put("/notifications/{notification_id}/read")
def mark_as_read(notification_id: int, current_user=Depends(get_current_user)):
    db = SessionLocal()

    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        db.close()
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True

    db.commit()
    db.close()

    return {"msg": "Notification marked as read"}



@router.delete("/notifications/{notification_id}")
def delete_notification(notification_id: int, current_user=Depends(get_current_user)):
    db = SessionLocal()

    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        db.close()
        raise HTTPException(status_code=404, detail="Notification not found")

    db.delete(notification)
    db.commit()
    db.close()

    return {"msg": "Notification deleted"}

