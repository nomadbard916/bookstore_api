from utils.const import (
    REDIS_URL,
    TOKEN_DESCRIPTION,
    TOKEN_INVALID_CREDENTIALS_MSG,
    TOKEN_SUMMARY,
)
from models.jwt_user import JWTUser
from datetime import datetime
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from starlette.status import HTTP_401_UNAUTHORIZED
from utils.security import authenticate_user, check_jwt_token, create_jwt_token
from fastapi import FastAPI
from starlette.requests import Request
from routes.v1 import app_v1
from routes.v2 import app_v2
from utils.db_object import db
import utils.redis_object as redis_object
from utils.redis_object import check_test_redis
import aioredis

app = FastAPI(
    title="Bookstore API Documentation",
    description="It is an API that is used for bookstores.",
    version="1.0.0",
)

app.include_router(
    app_v1,
    prefix="/v1",
    dependencies=[Depends(check_jwt_token), Depends(check_test_redis)],
)
app.include_router(
    app_v2,
    prefix="/v2",
    dependencies=[Depends(check_jwt_token), Depends(check_test_redis)],
)


@app.on_event("startup")
async def connect_db():
    await db.connect()
    redis_object.redis = await aioredis.create_redis_pool(REDIS_URL)


@app.on_event("shutdown")
async def disconnect_db():
    await db.disconnect()
    redis_object.redis.close()

    await redis_object.redis.wait_closed()


@app.post("/token", description=TOKEN_DESCRIPTION, summary=TOKEN_SUMMARY)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    jwt_user_dict = {"username": form_data.username, "password": form_data.password}
    jwt_user = JWTUser(**jwt_user_dict)
    user = await authenticate_user(jwt_user)

    user = authenticate_user(jwt_user)
    if user is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=TOKEN_INVALID_CREDENTIALS_MSG
        )

    jwt_token = create_jwt_token(user)

    return {"access_token": jwt_token}


@app.middleware("http")
async def middleware(request: Request, call_next):
    start_time = datetime.utcnow()

    response = await call_next(request)

    # modify response
    execution_time = (datetime.utcnow() - start_time).microseconds
    response.headers["x-execution_time"] = str(execution_time)

    return response
