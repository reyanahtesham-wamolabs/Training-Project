from __future__ import annotations
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine,select
from sqlalchemy.orm import Session
from Schema.models import User as dbUser 
from Schema.models import OTP as dbOTP 
from Models.PydModels import UserLogin,User
from Services.Hashing import hashPassword,checkPassword
from datetime import datetime, timedelta, UTC
engine = create_engine("postgresql+psycopg://reyan:1234@localhost:5432/mydb", echo=True)

load_dotenv()
OTP_EXPIRE_MINUTES=os.getenv("OTP_EXPIRE_MINUTES")
def addUser(data:User):
    User1=dbUser(ID=data.ID,password=data.password,role=data.role
    ,name=data.name,active=True,email=data.email,privacyLevel="High",SoftDelete=False)
    with Session(engine) as session:
        session.add(User1)
        session.commit()

def checkUser(data:UserLogin):
    with Session(engine) as session:
        stmt=select(dbUser).where(dbUser.email==data.email).where(dbUser.password==data.password)
        usersObj=session.scalars(stmt)    
        if usersObj:
            return usersObj
    return "User Not Found"        

def addOTP(OTPToAdd:str,email):
    with Session(engine) as session:
        OTPObject=dbOTP(Email=email,OTPString=OTPToAdd,ExpiresAt=datetime.now(UTC) + timedelta(minutes=OTP_EXPIRE_MINUTES) ,Attempts=0)
        session.add(OTPObject)
        session.commit()
    
def verifyOTP(OTPToCheck:str,email):
    with Session(engine) as session:
        flag=False
        desiredOTPObject=session.get(dbOTP,email)
        if desiredOTPObject:
            if desiredOTPObject.OTPString==OTPToCheck:
                flag=True
                session.delete(desiredOTPObject)
            else:
                desiredOTPObject.Attempts=desiredOTPObject.Attempts+1
                if desiredOTPObject.Attempts>2:
                    session.delete(desiredOTPObject)
            session.commit()
        return flag
    

