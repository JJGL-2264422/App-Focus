import json
import os
from tkinter import messagebox
from flask import Flask, request, redirect
from flask_restful import Resource, Api
import requests
import threading
from queue import Queue

facebook_login_result = None
google_login_result = None

app = Flask(__name__)
api = Api(app)

APP_ID = '1012742923698078'
APP_SECRET = '5615105aef5e25aa87825af75daa55ec'
FACEBOOK_REDIRECT_URI = 'http://localhost:5000/facebook/callback'

GOOGLE_CLIENT_ID = '686823449348-u5bvf5bnfka4n6gmg28k0jb93d8uqq0r.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'
GOOGLE_REDIRECT_URI = 'http://localhost:5000/google/callback'
GOOGLE_SCOPE = 'https://www.googleapis.com/auth/userinfo.profile'

class SaveTime(Resource):
    def post(self):
        time = request.json
        with open("salida.json", "w") as f:
            json.dump(time, f)

class Tareas(Resource):
    def get(self):
        if not os.path.exists("tareas.json"):
            messagebox.showinfo("Sin tareas", "No hay tareas guardadas")
            return

        with open("tareas.json", 'r') as f:
            tareas = json.load(f)
            return tareas

    def post(self):
        tarea = request.json
        if os.path.exists("tareas.json"):
            with open("tareas.json", 'r') as f:
                tareas = json.load(f)
        else:
            tareas = []

        tareas.append(tarea)

        with open("tareas.json", 'w') as f:
            json.dump(tareas, f, indent=6)
            
    def put(self):
        tareas = request.json
        with open("tareas.json", 'w') as f:
            json.dump(tareas, f,)


class FacebookLogin(Resource):
    def get(self):
        return redirect(f"https://www.facebook.com/v18.0/dialog/oauth?client_id={APP_ID}&redirect_uri={FACEBOOK_REDIRECT_URI}&scope=public_profile")

class FacebookCallback(Resource):
    def get(self):
        code = request.args.get('code')
        if not code:
            return "Error: No se recibió el código.", 400

        token_res = requests.get('https://graph.facebook.com/v18.0/oauth/access_token', params={
            'client_id': APP_ID,
            'redirect_uri': FACEBOOK_REDIRECT_URI,
            'client_secret': APP_SECRET,
            'code': code
        }).json()

        token = token_res.get('access_token')
        if not token:
            return "Error obteniendo token.", 400

        profile = requests.get(f'https://graph.facebook.com/me?fields=name&access_token={token}')
        name = profile.json().get("name", "Usuario")

        with open("info_usuario.json", "w") as f:
            json.dump({"nombre": name}, f)

        return f"Inicio de sesión exitoso"
    

class GoogleLogin(Resource):
    def get(self):
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?response_type=code"
            f"&client_id={GOOGLE_CLIENT_ID}"
            f"&redirect_uri={GOOGLE_REDIRECT_URI}"
            f"&scope={GOOGLE_SCOPE}"
        )
        return redirect(auth_url)

class GoogleCallback(Resource):
    def get(self):
        code = request.args.get('code')
        if not code:
            return "Error: No se recibió código de autorización.", 400

        token_url = 'https://oauth2.googleapis.com/token'
        data = {
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code'
        }

        token_res = requests.post(token_url, data=data).json()
        access_token = token_res.get('access_token')
        if not access_token:
            return "Error al obtener el token.", 400

        user_info = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        if user_info.status_code != 200:
            return "Error al obtener datos del perfil.", 400

        name = user_info.json().get("name", "Usuario")

        with open("info_usuario.json", "w") as f:
            json.dump({"nombre": name}, f)
        return f"Inicio de sesión exitoso"


api.add_resource(SaveTime, "/SaveTime")
api.add_resource(Tareas,"/Tareas")

api.add_resource(FacebookLogin, '/facebook')
api.add_resource(FacebookCallback, '/facebook/callback')

api.add_resource(GoogleLogin, "/google")
api.add_resource(GoogleCallback, "/google/callback")

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)