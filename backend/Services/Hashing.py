import bcrypt

def hashPassword(plainPassword):            
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(plainPassword.encode("utf-8"), salt)
    print(plainPassword)        
    return hashed_bytes.decode("utf-8")

def checkPassword(enteredPassword,hashedPassword):
    input1 = enteredPassword.encode('utf-8')
    input2=hashedPassword.encode('utf-8')
    if bcrypt.checkpw(input1,input2):
        return True
    return False

