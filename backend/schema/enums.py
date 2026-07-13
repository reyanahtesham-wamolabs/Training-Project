from enum import Enum

class Roles(Enum):
    admin="admin"
    member="member"

class Levels(Enum):
    low="low"
    medium="medium"
    high="high"
class Status(Enum):
    queued="queued"
    started="started"
    in_progress="in_progress"
    finished="finished"
    