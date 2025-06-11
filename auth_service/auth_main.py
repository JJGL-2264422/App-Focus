import json
import os
from datetime import datetime, timedelta
from typing import Optional
import mysql.connector

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

@app.post("/signup")
def register_user(username: str = Form(...), password: str = Form(...)):
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="bd_focus")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (user, contraseña) VALUES (%s,%s)",(f"{username}",f"{password}"))
        conn.commit()
        conn.close()
        return {"mensaje": "Usuario registrado"}
    except Exception as e:
        return JSONResponse(status_code=401, content={"error": f"No se pudo realizar la operación: {e}"})


@app.post("/token")
def login_token(username: str = Form(...), password: str = Form(...)):
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="", database="bd_focus")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE user = %s AND contraseña = %s",(f"{username}",f"{password}"))
        usuario = cursor.fetchone()
        if usuario:
            conn.close()
            token = create_access_token({"sub": username})
            return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        return JSONResponse(status_code=401, content={"error": f"No se pudo realizar la operación: {e}"})

    
    raise HTTPException(status_code=401, detail="Credenciales incorrectas")
