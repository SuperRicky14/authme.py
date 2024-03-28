import bcrypt

def hash_salt_password(password: str) -> bytes:
    """Returns a password that has been hashed and salted."""
    password_bytes = password.encode('utf-8') # low level array of the password string
    password_salt = bcrypt.gensalt() # generate a random salt

    # hash the password
    return bcrypt.hashpw(password_bytes, password_salt)

def check_correct_password(password: str, hashed_password: bytes):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)