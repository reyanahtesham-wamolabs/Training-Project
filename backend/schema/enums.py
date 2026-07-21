from enum import Enum

class Roles(Enum):
    admin="admin"
    manager="manager"
    member="member"
    Member="Member"
class Levels(Enum):
    low="low"
    medium="medium"
    high="high"
class ProjectStatus(Enum):
    planned="planned"
    started="started"
    in_progress="in_progress"
    finished="finished"
    under_review="under_review"
    archived="archived"
class Categories(Enum):
    upwork="upwork"
    US_based="US_based"
    Pak_profile="Pak_profile"
    inhouse="inhouse"
class AssignmentRole(Enum):
    project_admin="project_admin"
    project_member="project_member"
class OTPAction(Enum):
    verify_profile="verify_profile"
    change_password="change_password"
    change_email="change_email"
    change_name="change_name"
