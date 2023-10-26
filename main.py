from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from routers import sensors, auth
from routers.auth import get_current_user
import models
from database import engine
from starlette import status

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory='templates')


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = await get_current_user(request)
    return templates.TemplateResponse("home.html", {"request": request, "user": user})


app.include_router(sensors.router)
app.include_router(auth.router)
