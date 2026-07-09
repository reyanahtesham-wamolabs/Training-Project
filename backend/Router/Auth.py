from fastapi import APIRouter
from Project.backend.Models.UserModel import User,UserLogin,jwtTokensModel,CreateUser
from Repository.UserCRUD import UserCrud
router=APIRouter()



@router.post("/CreateUser/")
def CreateUser(userData:CreateUser):
    userCompleteData=User(name=userData.name,role=userData.role,password=userData.password,email=userData.email)
    UserCrud.Add_User(userCompleteData)    
    return userCompleteData
