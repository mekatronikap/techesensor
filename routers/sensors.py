import sys
from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette import status

import models
from database import SessionLocal
from routers.auth import get_current_user

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


async def is_own_sensor(request: Request, sensor_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)

    sensor_model = db.query(models.Sensors).filter(models.Sensors.id == sensor_id) \
        .filter(models.Sensors.owner_id == user.get("id")).first()

    return sensor_model


@router.get("/", response_class=HTMLResponse)
async def read_all_sensors(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    sensors = db.query(models.Sensors).filter(models.Sensors.owner_id == user.get("id")).all()
    return templates.TemplateResponse("sensors.html", {"request": request, "sensors": sensors, "user": user})


@router.get("/add-sensor", response_class=HTMLResponse)
async def add_sensor(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("new-sensor.html", {"request": request, "user": user})


@router.post("/add-sensor", response_class=HTMLResponse)
async def create_sensor(request: Request, db: Session = Depends(get_db), description: str = Form(...),
                        type: str = Form(...), site: str = Form(...),
                        equipment: str = Form(...), compartment: str = Form(...)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    sensor_model = models.Sensors()
    sensor_model.description = description
    sensor_model.type = type
    sensor_model.site = site
    sensor_model.equipment = equipment
    sensor_model.compartment = compartment
    sensor_model.owner_id = user.get("id")

    db.add(sensor_model)
    db.commit()

    return RedirectResponse(url="/sensors", status_code=status.HTTP_302_FOUND)


@router.get("/{sensor_id}", response_class=HTMLResponse)
async def read_sensor(request: Request, sensor_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    sensor = await is_own_sensor(request, sensor_id, db)
    if sensor is None:
        return RedirectResponse(url="/sensors", status_code=status.HTTP_302_FOUND)

    values = db.query(models.Values).filter(models.Values.sensor_id == sensor_id).all()
    return templates.TemplateResponse("sensor.html", {"request": request, "sensor": sensor, "user": user,
                                                      "values": values})


@router.get("/confirm-delete/{sensor_id}", status_code=status.HTTP_302_FOUND)
async def confirm_delete_sensor(request: Request, sensor_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/auth", status_code=status.HTTP_302_FOUND)

    sensor = await is_own_sensor(request, sensor_id, db)
    if sensor is None:
        return RedirectResponse(url="/sensors", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("delete-sensor.html", {"request": request, "sensor_id": sensor_id, "user": user})


@router.get("/delete/{sensor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sensor(request: Request, sensor_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/auth", status_code=status.HTTP_302_FOUND)

    sensor = await is_own_sensor(request, sensor_id, db)
    if sensor is None:
        return RedirectResponse(url="/sensors", status_code=status.HTTP_302_FOUND)

    db.query(models.Sensors).filter(models.Sensors.id == sensor_id).delete()
    db.commit()
    return RedirectResponse(url='/sensors', status_code=status.HTTP_302_FOUND)


@router.get("/edit/{sensor_id}", response_class=HTMLResponse)
async def edit_sensor(request: Request, sensor_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/auth", status_code=status.HTTP_302_FOUND)

    sensor = await is_own_sensor(request, sensor_id, db)
    if sensor is None:
        return RedirectResponse(url="/sensors", status_code=status.HTTP_302_FOUND)

    sensor = db.query(models.Sensors).filter(models.Sensors.id == sensor_id).first()
    return templates.TemplateResponse("edit-sensor.html", {"request": request, "sensor": sensor, "user": user})


@router.post("/edit/{sensor_id}", response_class=HTMLResponse)
async def edit_sensor_commit(request: Request, sensor_id: int, db: Session = Depends(get_db),
                             description: str = Form(...),
                             type: str = Form(...), site: str = Form(...),
                             equipment: str = Form(...), compartment: str = Form(...)):
    user = get_current_user(request)

    sensor = await is_own_sensor(request, sensor_id, db)
    if sensor is None:
        return RedirectResponse(url="/sensors", status_code=status.HTTP_302_FOUND)

    sensor_model = db.query(models.Sensors).filter(models.Sensors.id == sensor_id).first()
    sensor_model.description = description
    sensor_model.type = type
    sensor_model.site = site
    sensor_model.equipment = equipment
    sensor_model.compartment = compartment
    sensor_model.owner_id = 1

    db.add(sensor_model)
    db.commit()

    return RedirectResponse(url="/sensors", status_code=status.HTTP_302_FOUND)
