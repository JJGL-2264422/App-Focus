import json
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import JSONResponse
from jose import jwt

app = FastAPI()

SECRET_KEY = "clave-secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
USUARIOS_FILE = "../common/usuarios.json"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/token")
def login_token(username: str = Form(...), password: str = Form(...)):
    try:
        with open(USUARIOS_FILE, "r") as f:
            users = json.load(f)
    except FileNotFoundError:
        return JSONResponse(status_code=404, content={"error": "Archivo de usuarios no encontrado"})

    if username in users and users[username] == password:
        token = create_access_token({"sub": username})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Credenciales incorrectas")
