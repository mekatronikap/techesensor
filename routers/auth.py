import sys

from fastapi import APIRouter
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

sys.path.append("../..")

SECRET_KEY = "8decdd1e55908413191b5cf00583a0795b0859bd229b19c3516ab26e5775ca40"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"])

models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}
)

