import markdown
import uuid
import os
import shutil

from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from app.services.rag_service import create_vector_store, ask_pdf

from app.models.chat import (
    save_chat,
    get_user_conversations,
    get_conversation_chats_for_user,
    delete_conversation_for_user,
    delete_user_chats
)

from app.models.user import (
    update_user_profile,
    get_user_by_email
)

from app.services.ai_service import (
    get_ai_response,
    generate_conversation_title
)

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):

    user = request.session.get("user")

    if not user:
        return RedirectResponse(url="/login")

    conversation_id = request.cookies.get("conversation_id")

    conversations = get_user_conversations(user)

    if not conversation_id and conversations:
        conversation_id = conversations[0][0]

    if conversation_id:
        chats = get_conversation_chats_for_user(
            conversation_id,
            user
        )
    else:
        chats = []

    messages_html = ""

    for chat in chats:

        messages_html += f'''

        <div class="message user-message">

            <div class="message-header">
                <div class="avatar user-avatar">
                    U
                </div>

                <div>
                    <small>{chat[2]}</small><br>
                    <b>You:</b> {chat[0]}
                </div>
            </div>

        </div>

        <div class="message ai-message">

            <div class="message-header">

                <div class="avatar ai-avatar">
                    AI
                </div>

                <div>
                    <small>{chat[2]}</small><br>
                    <b>AI:</b>
                    {chat[1]}
                </div>

            </div>

        </div>

        '''

    response = templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "user": user,
            "messages_html": messages_html,
            "conversations": conversations,
            "active_conversation": conversation_id
        }
    )

    if conversation_id:
        response.set_cookie(
            key="conversation_id",
            value=conversation_id
        )

    return response


@router.post("/ask", response_class=HTMLResponse)
async def ask(
    request: Request,
    query: str = Form(...),
    file: UploadFile = File(None)
):

    user = request.session.get("user")
    conversation_id = request.cookies.get("conversation_id")

    if not user:
        return RedirectResponse(url="/login")

    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    if file and file.filename:

        if not file.filename.lower().endswith(".pdf"):

            return HTMLResponse(
                "<h3>Only PDF files are allowed.</h3>",
                status_code=400
            )

        content = await file.read()

        if not content.startswith(b"%PDF"):

            return HTMLResponse(
                "<h3>Invalid PDF file.</h3>",
                status_code=400
            )

        if len(content) > 10 * 1024 * 1024:

            return HTMLResponse(
                "<h3>PDF must be under 10 MB.</h3>",
                status_code=400
            )

        user_folder = f"uploads/{user}"

        os.makedirs(
            user_folder,
            exist_ok=True
        )

        file_path = os.path.join(
            user_folder,
            file.filename
        )

        with open(file_path, "wb") as f:
            f.write(content)

        create_vector_store(
            file_path,
            user
        )

        request.session["pdf_uploaded"] = True

    previous_chats = get_conversation_chats_for_user(
        conversation_id,
        user
    )

    if not previous_chats:
        conversation_title = generate_conversation_title(query)
    else:
        conversation_title = previous_chats[0][0][:40]

    pdf_uploaded = request.session.get("pdf_uploaded", False)

    if pdf_uploaded:

        raw_response = ask_pdf(
            query,
            user
        )

    else:

        raw_response = get_ai_response(
            query,
            previous_chats
        )

    current_time = datetime.now().strftime("%H:%M")

    save_chat(
        conversation_id,
        conversation_title,
        user,
        query,
        raw_response,
        current_time
    )

    response_obj = HTMLResponse(
        content=raw_response
    )

    response_obj.set_cookie(
        key="conversation_id",
        value=conversation_id
    )

    return response_obj


@router.get("/conversation/{conversation_id}")
def open_conversation(
    request: Request,
    conversation_id: str
):

    user = request.session.get("user")

    chats = get_conversation_chats_for_user(
        conversation_id,
        user
    )

    if not chats:
        return RedirectResponse(
            url="/dashboard",
            status_code=303
        )

    response = RedirectResponse(
        url="/chat",
        status_code=303
    )

    response.set_cookie(
        key="conversation_id",
        value=conversation_id
    )

    return response


@router.get("/new-chat")
def new_chat(request: Request):

    request.session["pdf_uploaded"] = False
    new_conversation_id = str(uuid.uuid4())

    response = RedirectResponse(
        url="/chat",
        status_code=303
    )

    response.set_cookie(
        key="conversation_id",
        value=new_conversation_id
    )

    return response

@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...)
):

    print("UPLOAD ROUTE HIT")

    return HTMLResponse("""
    <h1>UPLOAD SUCCESS</h1>
    """)


@router.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request):

    user = request.session.get("user")

    if not user:
        return RedirectResponse(url="/login")

    conversation_id = request.cookies.get("conversation_id")

    conversations = get_user_conversations(user)

    if not conversation_id and conversations:
        conversation_id = conversations[0][0]

    if conversation_id:
        chats = get_conversation_chats_for_user(
            conversation_id,
            user
        )
    else:
        chats = []

    messages_html = ""

    for chat in chats:

        messages_html += f'''

        <div class="message user-message">

            <div class="message-header">
                <div class="avatar user-avatar">
                    U
                </div>

                <div>
                    <small>{chat[2]}</small><br>
                    <b>You:</b> {chat[0]}
                </div>
            </div>

        </div>

        <div class="message ai-message">

            <div class="message-header">

                <div class="avatar ai-avatar">
                    AI
                </div>

                <div>
                    <small>{chat[2]}</small><br>
                    <b>AI:</b>
                    {markdown.markdown(chat[1])}
                </div>

            </div>

        </div>

        '''

    response = templates.TemplateResponse(
        request,
        "chat.html",
        {
            "user": user,
            "messages_html": messages_html,
            "conversations": conversations,
            "active_conversation": conversation_id
        }
    )

    if conversation_id:
        response.set_cookie(
            key="conversation_id",
            value=conversation_id
        )

    return response

@router.get("/analytics", response_class=HTMLResponse)
def analytics_page(request: Request):

    user = request.session.get("user")

    if not user:
        return RedirectResponse(url="/login")

    conversations = get_user_conversations(user)

    return templates.TemplateResponse(
        request,
        "analytics.html",
        {
            "user": user,
            "conversations": conversations
        }
    )

@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request):

    user_email = request.session.get("user")

    if not user_email:
        return RedirectResponse(url="/login")

    user_data = get_user_by_email(user_email)

    conversations = get_user_conversations(user_email)

    return templates.TemplateResponse(
        request,
        "settings.html",
        {
            "user": user_email,
            "username": user_data[3] if user_data[3] else "",
            "email": user_data[1],
            "conversations": conversations
        }
    )

@router.get("/delete-conversation/{conversation_id}")
def remove_conversation(
    request: Request,
    conversation_id: str
):

    user = request.session.get("user")

    delete_conversation_for_user(
        conversation_id,
        user
    )

    response = RedirectResponse(
        url="/dashboard",
        status_code=303
    )

    response.delete_cookie("conversation_id")

    return response

@router.get("/logout")
def logout(request: Request):

    request.session.clear()

    response = RedirectResponse(
        url="/login",
        status_code=303
    )

    response.delete_cookie("conversation_id")

    return response

@router.post("/update-profile")
async def update_profile(
    request: Request,
    username: str = Form(...),
    email: str = Form(...)
):

    current_email = request.session.get("user")

    update_user_profile(
        current_email,
        username,
        email
    )

    request.session["user"] = email

    return RedirectResponse(
        url="/settings",
        status_code=303
    )

@router.post("/clear-conversations")
def clear_conversations(request: Request):

    user = request.session.get("user")

    delete_user_chats(user)

    return RedirectResponse(
        url="/settings",
        status_code=303
    )