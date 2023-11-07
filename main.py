from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from routers import sensors, auth, values_api, auth_api
from routers.auth import get_current_user
import models
from database import engine, SessionLocal


app = FastAPI(docs_url=None, redoc_url=None)

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory='templates')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ValueRequest(BaseModel):
    temperature: int = Field()
    debris: int = Field(gte=0, lte=100)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = await get_current_user(request)
    if user:
        return RedirectResponse(url="/sensors", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("home.html", {"request": request, "user": user})


app.include_router(sensors.router)
app.include_router(auth.router)


sub_api = FastAPI()

sub_api.include_router(values_api.router)
sub_api.include_router(auth_api.router)

app.mount("/api", sub_api)
