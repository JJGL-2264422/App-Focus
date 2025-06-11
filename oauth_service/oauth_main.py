import json
import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from typing import Optional
from jose import jwt
from datetime import datetime, timedelta

app = FastAPI()
SECRET_KEY = "clave-secreta"
ALGORITHM = "HS256"

APP_ID = '1012742923698078'
APP_SECRET = '5615105aef5e25aa87825af75daa55ec'
FACEBOOK_REDIRECT_URI = 'http://localhost:8003/facebook/callback'

GOOGLE_CLIENT_ID = '686823449348-u5bvf5bnfka4n6gmg28k0jb93d8uqq0r.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'
GOOGLE_REDIRECT_URI = 'http://localhost:8003/google/callback'
GOOGLE_SCOPE = 'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email'

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.get("/facebook")
def login_facebook():
    url = (
        f"https://www.facebook.com/v18.0/dialog/oauth?"
        f"client_id={APP_ID}&redirect_uri={FACEBOOK_REDIRECT_URI}&scope=public_profile,email"
    )
    return RedirectResponse(url)

@app.get("/facebook/callback")
def callback_facebook(code: Optional[str] = None):
    if not code:
        return {"error": "No se recibió código"}

    token_res = requests.get('https://graph.facebook.com/v18.0/oauth/access_token', params={
        'client_id': APP_ID,
        'redirect_uri': FACEBOOK_REDIRECT_URI,
        'client_secret': APP_SECRET,
        'code': code
    }).json()

    access_token_fb = token_res.get('access_token')
    profile = requests.get(f'https://graph.facebook.com/me?fields=name,email&access_token={access_token_fb}')
    name = profile.json().get("name", "Usuario")
    email = profile.json().get("email", "Correo@gmail.com")

    jwt_token = create_access_token({"sub": name})

    with open("../common/info_usuario.json", "w") as f:
        json.dump({
            "nombre": name,
            "correo": email,
            "access_token": jwt_token
        }, f)

        return {
            "mensaje": "Inicio de sesión exitoso",
            "nombre": name,
            "correo": email,
            "access_token": jwt_token
        }

@app.get("/google")
def login_google():
    url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        f"&scope={GOOGLE_SCOPE}"
    )
    return RedirectResponse(url)

@app.get("/google/callback")
def callback_google(code: Optional[str] = None):
    if not code:
        return {"error": "No se recibió código"}

    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code'
    }

    token_res = requests.post(token_url, data=data).json()
    access_token_google = token_res.get('access_token')

    user_info = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {access_token_google}'}
    )

    name = user_info.json().get("name", "Usuario")
    email = user_info.json().get("email", "correo@desconocido.com")
    jwt_token = create_access_token({"sub": name})

    with open("../common/info_usuario.json", "w") as f:
        json.dump({
            "nombre": name,
            "correo": email,
            "access_token": jwt_token,
            "token_type": "bearer"
        }, f)

        return {
            "mensaje": "Inicio de sesión exitoso",
            "nombre": name,
            "correo": email,
            "access_token": jwt_token,
            "token_type": "bearer"
        }
