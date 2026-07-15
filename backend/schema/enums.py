from enum import Enum

class Roles(Enum):
    admin="admin"
    member="member"
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
