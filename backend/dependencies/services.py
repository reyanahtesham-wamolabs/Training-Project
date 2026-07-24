from fastapi import Depends
from dependencies.database import get_db

from services.user_management import UserManagementService
from services.project import ProjectService
from services.task import TaskService
from services.team import TeamService
from services.comment import CommentService
from services.activity_log import ActivityLogService
from services.notification import NotificationService
from services.auth import UserAuthenticationServices
from services.task_reminder import TaskReminderService

def get_user_service(db=Depends(get_db)) -> UserManagementService:
    return UserManagementService(db_session=db)

def get_project_service(db=Depends(get_db)) -> ProjectService:
    return ProjectService(db_session=db)

def get_task_service(db=Depends(get_db)) -> TaskService:
    return TaskService(db_session=db)

def get_team_service(db=Depends(get_db)) -> TeamService:
    return TeamService(db_session=db)

def get_comment_service(db=Depends(get_db)) -> CommentService:
    return CommentService(db_session=db)

def get_activity_log_service(db=Depends(get_db)) -> ActivityLogService:
    return ActivityLogService(db_session=db)

def get_notification_service(db=Depends(get_db)) -> NotificationService:
    return NotificationService(db_session=db)

def get_auth_service(db=Depends(get_db)) -> UserAuthenticationServices:
    return UserAuthenticationServices(db_session=db)

def get_task_reminder_service(db=Depends(get_db)) -> TaskReminderService:
    return TaskReminderService(db_session=db)
