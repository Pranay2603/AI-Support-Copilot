from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from app.models.user import (
    create_user,
    get_user,
    email_exists
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):

    return templates.TemplateResponse(
        request,
        "login.html",
        {}
    )


@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):

    return templates.TemplateResponse(
        request,
        "signup.html",
        {}
    )


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):

    user = get_user(email)

    if user and pwd_context.verify(password, user[2]):  

        response = RedirectResponse(
            url="/dashboard",
            status_code=303
        )

        request.session["user"] = email

        return response

    return templates.TemplateResponse(
        request,
        "login.html",
        {
            "error": "Invalid email or password."
        },
        status_code=400
    )

@router.post("/signup")
def signup(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):

    if email_exists(email):

        return templates.TemplateResponse(
            request,
            "signup.html",
            {
                "error": "Email already registered."
            }
        )

    hashed_password = pwd_context.hash(password)

    create_user(
        email,
        hashed_password
    )

    return RedirectResponse(
        url="/login",
        status_code=303
    )