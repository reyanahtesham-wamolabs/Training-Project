from fastapi import APIRouter
from Models.UserModel import User,CreateUser,UserLogin
from Repository.UserCRUD import UserCrud
router=APIRouter()


@router.post("/SignupUser/")
def Signup(userData:CreateUser):
    userCompleteData=User(name=userData.name,role=userData.role,password=userData.password,email=userData.email)
    UserCrud.add_user(userCompleteData)    
    return userCompleteData

@router.post("/Login/")
def Login(userData:UserLogin):
    if not UserCrud.user_login(userData) == "User Not Found":
        return userData
    return ""

