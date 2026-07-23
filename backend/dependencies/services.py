from fastapi import Depends
from dependencies.database import get_db

from services.user_services_management import UserManagementService
from services.project_services import ProjectService
from services.task_services import TaskService
from services.team_service import TeamService
from services.comment_services import CommentService
from services.activity_log_services import ActivityLogService
from services.notification_service import NotificationService
from services.auth_services import UserAuthenticationServices

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
