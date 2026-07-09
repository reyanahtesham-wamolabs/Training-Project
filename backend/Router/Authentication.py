from fastapi import APIRouter
from Models.UserModel import User,CreateUser,UserLogin
from Repository.UserCRUD import UserCrud
from Services.UserServices import UserAuthenticationServces
router=APIRouter()


@router.post("/SignupUser/")
def Signup(userData:CreateUser):
    userCompleteData=UserAuthenticationServces.user_signup(userData)
    return userCompleteData

@router.post("/Login/")
def Login(userData:UserLogin):
    data=UserAuthenticationServces.user_login(userData)
    return data

