import bcrypt

def hash_password(plainPassword):            
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(plainPassword.encode("utf-8"), salt)
    return hashed_bytes.decode("utf-8")

