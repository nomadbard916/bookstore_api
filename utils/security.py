from fastapi import Depends, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordBearer
import jwt
from utils.const import (
    JWT_ALGORITH,
    JWT_EXPIRATION_TIME_MINUTES,
    JWT_INVALID_MSG,
    JWT_SECRET_KEY,
)
from models.jwt_user import JWTUser
from passlib.context import CryptContext
from datetime import datetime, timedelta
import time
from starlette.status import HTTP_401_UNAUTHORIZED
from utils.db_functions import db_check_token_user, db_check_jwt_username

pwd_context = CryptContext(schemes="bcrypt")
oauth_schema = OAuth2PasswordBearer(tokenUrl="/token")


def get_hashed_password(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(e)
        return False


# Authenticate username and password to give JWT token
async def authenticate_user(db_user: JWTUser):
    potential_users = await db_check_token_user(db_user)
    is_valid = False

    for db_user in potential_users:
        if verify_password(db_user.password, db_user["password"]):
            is_valid = True

    if is_valid:
        db_user.role = "admin"
        return db_user

    return None


# Create access JWT token
def create_jwt_token(user: JWTUser):
    expiration = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_TIME_MINUTES)
    jwt_payload = {"sub": user.username, "role": user.role, "exp": expiration}
    jwt_token = jwt.encode(jwt_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITH)

    return jwt_token


# Check whether JWT token is correct
async def check_jwt_token(token: str = Depends(oauth_schema)):
    try:
        jwt_payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=JWT_ALGORITH)
        username = jwt_payload.get("sub")
        role = jwt_payload.get("role")
        expiration = jwt_payload.get("exp")

        if time.time() < expiration:
            is_valid = await db_check_jwt_username(username)
            if is_valid:
                return final_checks(role)

    except Exception:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)


# Last checking and returning the final result
def final_checks(role: str):
    if role == "admin":
        return True
    else:
        return HTTPException(status_code=HTTP_401_UNAUTHORIZED)
