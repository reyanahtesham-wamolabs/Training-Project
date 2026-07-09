import bcrypt

def hashPassword(plainPassword):            
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(plainPassword.encode("utf-8"), salt)
    print(plainPassword)        
    return hashed_bytes.decode("utf-8")

