from fastapi import APIRouter, Depends, HTTPException, Security
from starlette import status
from pydantic import BaseModel
from starlette.requests import Request
from fastapi.security import APIKeyHeader

import models
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from models import Sensors, Values
from routers.auth_api import get_current_user, get_user


api_keys = [
    "my_api_key"
]

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
api_key_header = APIKeyHeader(name='X-API-Key')


class ValueRequest(BaseModel):
    temperature: int
    debris: int


def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if api_key_header in api_keys:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key"
    )


@router.post("/{username}/{sensor_id}", status_code=status.HTTP_201_CREATED)
async def send_value(request: Request, value_request: ValueRequest, username: str, sensor_id: int, db: db_dependency, api_key: str = Security(get_api_key)):
    user = get_user(username=username, db=db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    sensor = db.query(models.Sensors).filter(models.Sensors.id == sensor_id) \
        .filter(models.Sensors.owner_id == user.id).first()

    if sensor is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    value_model = Values(**value_request.model_dump(), sensor_id=sensor_id)

    db.add(value_model)
    db.commit()


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



