from .database import get_db
from fastapi import Depends
from services.user_services_management import UserManagementService

def get_user_service(db=Depends(get_db)) -> UserManagementService:
    return UserManagementService(db_session=db)
