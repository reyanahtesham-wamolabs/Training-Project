from fastapi import FastAPI, Depends, APIRouter,BackgroundTasks,Request
from fastapi.middleware.cors import CORSMiddleware
# from ..Models.PydModels import User,UserLogin
from Models.PydModels import User,UserLogin,jwtTokensModel,CreateUser
from Repository.UserCRUD import addUser,verifyOTP as verifyOTPFromDB, checkUser,addOTP as addOTPToDB
from Services.OTPGen import GenerateOTP,emailOTP
from Services.jwtTokens import create_access_token,create_refresh_token,decode_token
router=APIRouter()


@router.get("/")
def home():
    return {"message": "Hello World"}

@router.post("/Login/")
def Login(userData:UserLogin):
    if not checkUser(userData) == "User Not Found":
        return userData
    return "Email Password Correct. Verify OTP"


@router.post("/CreateUser/")
def CreateUser(userData:CreateUser):
    userCompleteData=User(name=userData.name,role=userData.role,password=userData.password,email=userData.email)
    addUser(userCompleteData)    
    return userCompleteData

@router.post("/getOTP/")
def getOTP(Email):
    otp=GenerateOTP()
    emailOTP(otp,Email)
    
@router.post("/VerifyOtp/")
def VerifyOTP(OTP,Email):
    flag=verifyOTPFromDB(OTP,Email)
    if flag:
        aToken=create_access_token(email=Email)
        rToken=create_refresh_token(email=Email)

    return jwtTokensModel(access_token=aToken,refresh_token=rToken)
    
