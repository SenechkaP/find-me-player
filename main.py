from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import Optional

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
def register(
        name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        age: Optional[str] = Form(None)
):
    age_param = f"&age={age}" if age and age.isdigit() else ""
    return RedirectResponse(url=f"/profile?name={name}&email={email}{age_param}", status_code=303)


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
