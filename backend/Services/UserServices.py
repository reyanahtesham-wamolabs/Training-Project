from Models.UserModel import User,CreateUser,UserLogin
from Repository.UserCRUD import UserCrud


class UserAuthenticationServces:
    def user_signup(userData:CreateUser):
        userCompleteData=User(name=userData.name,role=userData.role,password=userData.password,email=userData.email)
        UserCrud.add_user(userCompleteData)    
        return userCompleteData

    def user_login(userData:UserLogin):
        if not UserCrud.check_user(userData) == "User Not Found":
            return userData
        return ""
