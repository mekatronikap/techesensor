import sys
from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette import status

import models
from database import SessionLocal

sys.path.append("..")


router = APIRouter(
    prefix="/sensors",
    tags=["sensors"],
    responses={404: {"description": "Not found"}}
)

templates = Jinja2Templates(directory='templates')


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
async def read_all_sensors(request: Request, db: Session = Depends(get_db)):
    # todos auth
    sensors = db.query(models.Sensors).all()
    return templates.TemplateResponse("sensors.html", {"request": request, "sensors": sensors})


@router.get("/add-sensor", response_class=HTMLResponse)
async def add_sensor(request: Request):
    return templates.TemplateResponse("new-sensor.html", {"request": request})


@router.post("/add-sensor", response_class=HTMLResponse)
async def create_sensor(request: Request, db: Session = Depends(get_db), description: str = Form(...),
                        type: str = Form(...), site: str = Form(...),
                        equipment: str = Form(...), compartment: str = Form(...)):
    #   todos authentication
    sensor_model = models.Sensors()
    sensor_model.description = description
    sensor_model.type = type
    sensor_model.site = site
    sensor_model.equipment = equipment
    sensor_model.compartment = compartment
    sensor_model.owner_id = 1

    db.add(sensor_model)
    db.commit()

    return RedirectResponse(url="/sensors", status_code=status.HTTP_302_FOUND)


@router.get("/{sensor_id}", response_class=HTMLResponse)
async def read_sensor(request: Request, sensor_id: int, db: Session = Depends(get_db)):
    # Todo auth
    sensor = db.query(models.Sensors).filter(models.Sensors.id == sensor_id).first()
    return templates.TemplateResponse("sensor.html", {"request": request, "sensor": sensor})


@router.get("/delete/{sensor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sensor(request: Request, sensor_id: int, db: Session = Depends(get_db)):
    # todo auth
    sensor_model = db.query(models.Sensors).filter(models.Sensors.id == sensor_id).first()

    if sensor_model is None:
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

    db.query(models.Sensors).filter(models.Sensors.id == sensor_id).delete()
    db.commit()
    return RedirectResponse(url='/sensors', status_code=status.HTTP_302_FOUND)

