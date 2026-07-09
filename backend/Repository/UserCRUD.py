from __future__ import annotations
from dotenv import load_dotenv
from sqlalchemy import create_engine,select
from sqlalchemy.orm import Session
from Project.backend.Schema.UserModels import User as db_User 
from Project.backend.Schema.UserModels import OTP as dbOTP 
from Project.backend.Models.UserModel import User
engine = create_engine("postgresql+psycopg://reyan:1234@localhost:5432/mydb", echo=True)

class UserCrud:
    def Add_User(data:User):
        User1=db_User(ID=data.ID,password=data.password,role=data.role,name=data.name,active=True,email=data.email,privacyLevel="High",SoftDelete=False)
        with Session(engine) as session:
            session.add(User1)
            session.commit()