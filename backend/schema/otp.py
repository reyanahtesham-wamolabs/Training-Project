from __future__ import annotations
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column,relationship
from .baseclass import Base
from .enums import OTPAction
from sqlalchemy import Enum as sa_enum,ForeignKey,DateTime
from sqlalchemy import String
from datetime import datetime,timezone,timedelta
import uuid
from datetime import datetime, timedelta, UTC
import os
from dotenv import load_dotenv
load_dotenv()

OPT_EXPIRE_MINUTES=int(os.getenv("OTP_EXPIRE_MINUTES"))



class OTP(Base):
    __tablename__ = "OTP"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    code:Mapped[str]
    valid_till: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(minutes=OPT_EXPIRE_MINUTES),
    )
    user_id: Mapped[str] = mapped_column(String, ForeignKey("User.id"), nullable=False)
    user_name: Mapped[str] = mapped_column(String, nullable=False)
    new_desired_password:Mapped[str]=mapped_column(String,nullable=True)
    new_desired_name:Mapped[str]=mapped_column(String,nullable=True)
    new_desired_email:Mapped[str]=mapped_column(String,nullable=True)
    user = relationship("User")
    action:Mapped[OTPAction]=mapped_column(sa_enum(OTPAction))
