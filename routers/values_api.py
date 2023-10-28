from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette import status
from pydantic import BaseModel
from starlette.requests import Request

import models
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from models import Sensors, Values
from routers.auth_api import get_current_user


router = APIRouter(
    prefix='/values',
    tags=['values']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]


class ValueRequest(BaseModel):
    temperature: int
    debris: int


@router.get("/", status_code=status.HTTP_200_OK)
async def get_values(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    return db.query(models.Values).all()


@router.post("/sensors/{sensor_id}", status_code=status.HTTP_201_CREATED)
async def post_value(request: Request, value_request: ValueRequest, sensor_id: int,
                     user: user_dependency, db: db_dependency):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    sensor = db.query(models.Sensors).filter(models.Sensors.id == sensor_id) \
        .filter(models.Sensors.owner_id == user.id).first()
    if sensor is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    value_model = Values(**value_request.model_dump(), sensor_id=sensor_id)

    db.add(value_model)
    db.commit()
