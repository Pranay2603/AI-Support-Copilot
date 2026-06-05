from fastapi import FastAPI, Request
from dotenv import load_dotenv
import os
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from app.routes import dashboard
from app.models.chat import create_chat_table
from app.routes import auth

load_dotenv()
app = FastAPI()

@app.middleware("http")
async def add_no_cache_headers(
    request: Request,
    call_next
):

    response = await call_next(request)

    response.headers["Cache-Control"] = (
        "no-cache, no-store, must-revalidate"
    )

    response.headers["Pragma"] = "no-cache"

    response.headers["Expires"] = "0"

    return response

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY")
)

create_chat_table()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth.router)
app.include_router(dashboard.router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )


# .\venv\Scripts\Activate
# uvicorn app.main:app --reload