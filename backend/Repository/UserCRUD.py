from __future__ import annotations
from dotenv import load_dotenv
from sqlalchemy import create_engine,select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from Schema.UserModels import User as db_User 
from Models.UserModel import User,UserLogin
engine = create_engine("postgresql+psycopg://reyan:1234@localhost:5432/mydb", echo=True)

class UserCrud:
    def add_user(data:User):
        User1=db_User(ID=data.ID,password=data.password,role=data.role,name=data.name,active=True,email=data.email,privacyLevel="High",SoftDelete=False)
        with Session(engine) as session:
            try:
                session.add(User1)
                session.commit()
                return User1
            except SQLAlchemyError:
                session.rollback()
                raise

    def user_login(data:UserLogin):
        with Session(engine) as session:
            try:
                stmt = select(db_User).where(
                    db_User.email == data.email,
                    db_User.password == data.password
                )
                usersObj=session.scalars(stmt)    
                if usersObj is None:
                    raise ValueError("User not found")
                return usersObj
            except SQLAlchemyError:
                raise



