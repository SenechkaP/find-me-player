from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse

from constances import make_tg_message
from models import User, UserRegister, UserLogin, TeamForm
from sqlalchemy.orm import Session
from database import get_db
from env_values import chat_id, TELEGRAM_API_URL
from games_data import get_nba_games
import requests

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
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже используется")

    new_user = User(name=user.name, email=user.email, age=user.age)
    new_user.set_password(user.password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url=f"/profile?name={user.name}&email={user.email}&age={user.age}", status_code=303)


@app.post("/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if not existing_user or not existing_user.verify_password(user.password):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")

    return RedirectResponse(
        url=f"/profile?name={existing_user.name}&email={existing_user.email}&age={existing_user.age}", status_code=303)


@app.get("/profile")
def get_profile_page(request: Request, name: str, email: str, age: int = None):
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "name": name,
        "email": email,
        "age": age
    })


@app.get("/team_form")
async def form_page(request: Request):
    return templates.TemplateResponse("team_form.html", {"request": request})


@app.post("/team_form/submit")
async def submit_form(form_data: TeamForm):
    try:
        message = make_tg_message(form_data)
        data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

        response = requests.post(TELEGRAM_API_URL, data=data)
        response.raise_for_status()

        return JSONResponse(
            status_code=200,
            content={"status": "ok", "message": "Заявка отправлена!"}
        )

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при отправке в Telegram: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сервера: {str(e)}"
        )


@app.get("/nba_games")
async def show_nba_games(request: Request):
    games_data = await get_nba_games()
    response = templates.TemplateResponse(
        "games.html",
        {
            "request": request,
            "days": games_data
        }
    )

    response.headers["Cache-Control"] = "public, max-age=3600"

    return response
