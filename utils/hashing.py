from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    # Bcrypt has a 72 byte limit. Passlib 1.7+ usually handles this but 
    # explicitly truncating prevents "ValueError: password cannot be longer than 72 bytes"
    # in some environments or with certain backends.
    if plain_password:
        plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)
