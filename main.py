from fastapi import FastAPI, Request, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse

from constances import make_tg_message
from jwt_config import create_access_token, verify_token
from uuid import UUID
from models import User, Post, Like, UserRegister, UserLogin, UserPost, TeamForm
from sqlalchemy.orm import Session
from database import get_db
from env_values import chat_id, TELEGRAM_API_URL
from games_data import get_nba_games
from typing import List
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

    token = create_access_token({"sub": str(new_user.id)})

    response = RedirectResponse(url="/profile", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True)

    return response


@app.post("/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if not existing_user or not existing_user.verify_password(user.password):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")

    token = create_access_token({"sub": str(existing_user.id)})

    response = RedirectResponse(url="/profile", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True)

    return response


@app.get("/logout")
def logout():
    response = RedirectResponse(url="/auth")
    response.delete_cookie("access_token")
    return response


@app.get("/profile")
def get_profile_page(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth")

    payload = verify_token(token)
    if not payload:
        return RedirectResponse(url="/auth")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == UUID(user_id)).first()
    if not user:
        return RedirectResponse(url="/auth")

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "name": user.name,
        "email": user.email,
        "age": user.age
    })


@app.post("/profile/create_post")
async def create_post(user_post: UserPost, request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неавторизован")

    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный токен")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ошибка пользователя")

    new_post = Post(user_id=user_id, content=user_post.content)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return JSONResponse(status_code=201, content={"message": "Пост создан"})


@app.get("/profile/posts")
def my_posts(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    payload = verify_token(token)
    if not payload:
        return RedirectResponse("/auth")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == UUID(user_id)).first()
    posts = db.query(Post).filter(Post.user_id == UUID(user_id)).order_by(Post.created_at.desc()).all()

    return templates.TemplateResponse("user_posts.html", {
        "request": request,
        "name": user.name,
        "posts": posts,
    })


@app.get("/posts")
def all_posts(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    payload = verify_token(token)
    if not payload:
        return RedirectResponse("/auth")

    user_id = payload.get("sub")
    posts = db.query(Post).order_by(Post.created_at.desc()).all()

    return templates.TemplateResponse("all_posts.html", {
        "request": request,
        "posts": posts,
        "user_id": user_id
    })


@app.post("/posts/{post_id}/like")
async def like_post(post_id: UUID, request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Неавторизован")

    user_id = payload.get("sub")
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    like = db.query(Like).filter_by(user_id=user_id, post_id=post_id).first()

    if like:
        db.delete(like)
        post.likes -= 1
    else:
        db.add(Like(user_id=user_id, post_id=post_id))
        post.likes += 1

    db.commit()

    post = db.query(Post).get(post_id)

    await manager.broadcast({
        "post_id": str(post_id),
        "likes": post.likes
    })

    return {"post_id": str(post_id), "likes": post.likes}


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


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@app.websocket("/ws/likes")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
