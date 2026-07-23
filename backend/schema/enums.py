from enum import Enum


class Roles(Enum):
    admin = "admin"
    manager = "manager"
    member = "member"


class Levels(Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ProjectStatus(Enum):
    planned = "planned"
    started = "started"
    in_progress = "in_progress"
    finished = "finished"
    under_review = "under_review"
    archived = "archived"


class Categories(Enum):
    upwork = "upwork"
    US_based = "US_based"
    Pak_profile = "Pak_profile"
    inhouse = "inhouse"


class AssignmentRole(Enum):
    project_admin = "project_admin"
    project_member = "project_member"


class OTPAction(Enum):
    verify_profile = "verify_profile"
    change_password = "change_password"
    change_email = "change_email"
    change_name = "change_name"


class ActivityActionType(Enum):
    create_project = "create_project"
    update_project = "update_project"
    archive_project = "archive_project"
    delete_project = "delete_project"
    create_tag = "create_tag"
    create_task = "create_task"
    update_task = "update_task"
    delete_task = "delete_task"
    add_prerequisite = "add_prerequisite"
    create_user = "create_user"
    update_user = "update_user"
    delete_user = "delete_user"
    modify_user_status = "modify_user_status"
    change_user_privacy = "change_user_privacy"
    assign_user = "assign_user"

