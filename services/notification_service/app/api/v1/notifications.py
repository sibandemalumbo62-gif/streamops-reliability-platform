from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.dependencies import get_db
from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    BulkNotificationCreate
)
from app.repositories.notification_repository import (
    create_notification,
    get_notification_by_id,
    get_user_notifications,
    update_notification,
    mark_as_read,
    mark_all_as_read
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.post("/", response_model=NotificationResponse, status_code=201)
def create_notification_endpoint(
    notification: NotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        new_notification = create_notification(db, notification.model_dump())
        
        # In production, this would trigger background task to send notification
        # background_tasks.add_task(send_notification_task, new_notification.id)
        
        return new_notification
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create notification: {str(error)}"
        )


@router.post("/bulk")
def create_bulk_notifications(
    bulk: BulkNotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        created_notifications = []
        for user_id in bulk.user_ids:
            notification_data = bulk.model_dump(exclude={"user_ids"})
            notification_data["user_id"] = user_id
            new_notification = create_notification(db, notification_data)
            created_notifications.append(new_notification)
        
        return {
            "message": f"Created {len(created_notifications)} notifications",
            "count": len(created_notifications)
        }
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create bulk notifications: {str(error)}"
        )


@router.get("/user/{user_id}", response_model=List[NotificationResponse])
def get_user_notifications_endpoint(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    try:
        notifications = get_user_notifications(db, user_id, skip, limit, unread_only)
        return notifications
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch notifications: {str(error)}"
        )


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification_endpoint(
    notification_id: str,
    db: Session = Depends(get_db)
):
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )
    return notification


@router.patch("/{notification_id}", response_model=NotificationResponse)
def update_notification_endpoint(
    notification_id: str,
    notification_update: NotificationUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated_notification = update_notification(
            db,
            notification_id,
            notification_update.model_dump(exclude_unset=True)
        )
        if not updated_notification:
            raise HTTPException(
                status_code=404,
                detail="Notification not found"
            )
        return updated_notification
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update notification: {str(error)}"
        )


@router.post("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: str,
    db: Session = Depends(get_db)
):
    try:
        notification = mark_as_read(db, notification_id)
        if not notification:
            raise HTTPException(
                status_code=404,
                detail="Notification not found"
            )
        return {"message": "Notification marked as read"}
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to mark notification as read: {str(error)}"
        )


@router.post("/user/{user_id}/read-all")
def mark_all_as_read_endpoint(
    user_id: str,
    db: Session = Depends(get_db)
):
    try:
        count = mark_all_as_read(db, user_id)
        return {
            "message": f"Marked {count} notifications as read",
            "count": count
        }
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to mark all as read: {str(error)}"
        )
