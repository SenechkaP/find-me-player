from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from models import UserRegister
from dotenv import load_dotenv
import requests
import os

load_dotenv()

app = FastAPI()

app.mount("/src", StaticFiles(directory="src"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
def get_main_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/rights")
def get_rights_page(request: Request):
    return templates.TemplateResponse("rights.html", {"request": request})


@app.get("/auth")
def get_auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


@app.post("/auth/register")
def register(user: UserRegister):
    age_param = f"&age={user.age}" if user.age else ""
    return RedirectResponse(url=f"/profile?name={user.name}&email={user.email}{age_param}", status_code=303)


@app.post("/auth/login")
def login(email: str = Form(...), password: str = Form(...)):
    pass
    # запрос в бд за данными
    # return RedirectResponse(url=f"/profile?email={email}", status_code=303)


@app.get("/profile")
def get_profile_page(request: Request, name: str, email: str, age: int = None):
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "name": name,
        "email": email,
        "age": age
    })


@app.get("/form")
async def form_page(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


chat_id = os.getenv("CHAT_ID")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"


@app.post("/form/submit")
async def submit_form(
        team_name: str = Form(...),
        player1: str = Form(...),
        player2: str = Form(...),
        player3: str = Form(...),
        player4: str = Form(...),
        player5: str = Form(...),
):
    message = (
        f"🏀 Новая заявка на турнир!\n\n"
        f"📌 *Команда:* {team_name}\n\n"
        f"👤 *Игроки:*\n"
        f"1️⃣ {player1}\n"
        f"2️⃣ {player2}\n"
        f"3️⃣ {player3}\n"
        f"4️⃣ {player4}\n"
        f"5️⃣ {player5}"
    )

    data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    response = requests.post(TELEGRAM_API_URL, data=data)

    if response.status_code == 200:
        return {"status": "ok", "message": "Заявка отправлена!"}
    else:
        return {"status": "error", "message": "Ошибка отправки!"}
