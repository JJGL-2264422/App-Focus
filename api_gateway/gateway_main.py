from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
import requests

app = FastAPI()
class Tiempo(BaseModel):
    nombre: str
    tiempo: str

@app.post("/login")
async def login(request: Request):
    form = await request.form()
    res = requests.post("http://localhost:8001/token", data=form)
    return JSONResponse(status_code=res.status_code, content=res.json())

@app.post("/signup")
async def login(request: Request):
    form = await request.form()
    res = requests.post("http://localhost:8001/signup", data=form)
    return JSONResponse(status_code=res.status_code, content=res.json())

@app.get("/Tareas")
def get_tareas(request: Request):
    auth = request.headers.get("authorization")
    res = requests.get("http://localhost:8002/tareas", headers={"Authorization": auth})
    return JSONResponse(status_code=res.status_code, content=res.json())

@app.post("/Tareas")
async def post_tareas(request: Request):
    auth = request.headers.get("authorization")
    data = await request.json()
    res = requests.post("http://localhost:8002/tareas", headers={"Authorization": auth}, json=data)
    return JSONResponse(status_code=res.status_code, content=res.json())

@app.post("/SaveTime")
async def post_time(tiempo: Tiempo, authorization: str = Header(...)):
    res = requests.post("http://localhost:8002/tiempo", headers={"Authorization": authorization}, json=tiempo.dict())
    return JSONResponse(status_code=res.status_code, content=res.json())

@app.get("/facebook")
def redir_facebook():
    return RedirectResponse("http://localhost:8003/facebook")

@app.get("/facebook/callback")
def facebook_callback(code: str):
    res = requests.get("http://localhost:8003/facebook/callback", params={"code": code})
    return JSONResponse(content=res.json())

@app.get("/google")
def redir_google():
    return RedirectResponse("http://localhost:8003/google")

@app.get("/google/callback")
def google_callback(code: str):
    res = requests.get("http://localhost:8003/google/callback", params={"code": code})
    return JSONResponse(content=res.json())
