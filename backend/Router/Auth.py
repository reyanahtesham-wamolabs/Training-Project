from fastapi import APIRouter
from Models.UserModel import User,CreateUser
from Repository.UserCRUD import UserCrud
router=APIRouter()


@router.post("/SignupUser/")
def Signup(userData:CreateUser):
    userCompleteData=User(name=userData.name,role=userData.role,password=userData.password,email=userData.email)
    UserCrud.Add_User(userCompleteData)    
    return userCompleteData

