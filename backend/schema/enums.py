from enum import Enum

class Roles(Enum):
    Admin="Admin"
    Member="Member"

class Categories(Enum):
    Upwork="Upwork"
    Contract="Contract"
    US_profile="US_profile"
    pk_profile="pk_profile"

class ProjectStatus(Enum):
    Planned="Planned"
    Active="Active"
    Archived="Archived"
    Completed="Completed"
    
class Levels(Enum):
    high="high"
    medium="medium"
    low="low"

