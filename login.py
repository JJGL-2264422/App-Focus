import tkinter as tk
from tkinter import messagebox
import json
import os
import requests
from flask import Flask, request, redirect, render_template_string
import threading
import webbrowser
from queue import Queue

import tarea

#JSON
DATA_FILE = 'usuarios.json'
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

# Funciones

'''def mostrar_bienvenida(usuario):
    ventana_bienvenida = tk.Toplevel()
    ventana_bienvenida.title("Bienvenido")
    ventana_bienvenida.geometry("1200x800")

    frame = tk.Frame(ventana_bienvenida)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame, text=f"¡Bienvenido, {usuario}!", font=("Arial", 32)).pack(pady=40)
    tk.Button(frame, text="Cerrar sesión", font=("Arial", 18), width=20,
              command=lambda: cerrar_sesion(ventana_bienvenida)).pack(pady=20)
'''
def cerrar_sesion(ventana_actual):
    ventana_actual.destroy()
    ventana_principal.deiconify()

def registrar_usuario():
    usuario = entry_usuario_registro.get()
    contraseña = entry_contraseña_registro.get()

    if not usuario or not contraseña:
        messagebox.showwarning("Campos vacíos", "Por favor, completa todos los campos.")
        return

    with open(DATA_FILE, 'r') as f:
        usuarios = json.load(f)

    if usuario in usuarios:
        messagebox.showerror("Error", "El usuario ya existe.")
        return

    usuarios[usuario] = contraseña
    with open(DATA_FILE, 'w') as f:
        json.dump(usuarios, f)

    messagebox.showinfo("Éxito", "Usuario registrado exitosamente.")
    ventana_registro.destroy()

def iniciar_sesion():
    usuario = entry_usuario_login.get()
    contraseña = entry_contraseña_login.get()

    with open(DATA_FILE, 'r') as f:
        usuarios = json.load(f)

    if usuario in usuarios and usuarios[usuario] == contraseña:
        ventana_login.destroy()
        ventana_principal.destroy()
        tarea.dashboard(usuario)
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

#Inicio por facebook
facebook_login_result = Queue()
def iniciar_facebook():
    threading.Thread(target=run_flask_server, daemon=True).start()
    threading.Timer(1.5, lambda: webbrowser.open('http://localhost:5000')).start()
    ventana_principal.after(100, revisar_loginface)

def revisar_loginface():
    if not facebook_login_result.empty():
        nombre = facebook_login_result.get()
        if nombre:
            ventana_login.destroy()
            ventana_principal.destroy()
            tarea.dashboard(nombre)
        else:
            messagebox.showerror("Error", "No se pudo iniciar sesión con Facebook.")
    else:
        ventana_principal.after(100, revisar_loginface)

#Servidor Flask (Facebook)
app = Flask(__name__)

APP_ID = '1012742923698078'
APP_SECRET = '5615105aef5e25aa87825af75daa55ec'
REDIRECT_URI = 'http://localhost:5000/callback'

@app.route('/')
def loginface():
    auth_url = f'https://www.facebook.com/v18.0/dialog/oauth?client_id={APP_ID}&redirect_uri={REDIRECT_URI}&scope=public_profile'
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        facebook_login_result.put(None)
        return "Error: No se recibió el código de autorización.", 400

    token_url = 'https://graph.facebook.com/v18.0/oauth/access_token'
    params = {
        'client_id': APP_ID,
        'redirect_uri': REDIRECT_URI,
        'client_secret': APP_SECRET,
        'code': code
    }

    token_response = requests.get(token_url, params=params)
    token_data = token_response.json()
    access_token = token_data.get('access_token')

    if not access_token:
        facebook_login_result.put(None)
        return "Error obteniendo el token.", 400

    profile_url = f'https://graph.facebook.com/v18.0/me?access_token={access_token}&fields=name'
    profile_response = requests.get(profile_url)

    if profile_response.status_code == 200:
        name = profile_response.json().get("name", "Usuario")
        facebook_login_result.put(name)
    else:
        facebook_login_result.put(None)
        return "Error al obtener el perfil.", 400
    return "Inicio de sesión exitoso. Puedes cerrar esta pestaña."

def run_flask_server():
    app.run(port=5000)

#Inicio por Google
google_login_result = Queue()
def iniciar_google():
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Timer(1.5, lambda: webbrowser.open('http://localhost:5000/google')).start()
    ventana_principal.after(100, revisar_logingoogle)

def revisar_logingoogle():
    if not google_login_result.empty():
        nombre = google_login_result.get()
        if nombre:
            ventana_login.destroy()
            ventana_principal.destroy()
            tarea.dashboard(nombre)
        else:
            messagebox.showerror("Error", "No se pudo iniciar sesión con Google.")
    else:
        ventana_principal.after(100, revisar_logingoogle)

#Servidor Flask (Google)
app = Flask(__name__)

GOOGLE_CLIENT_ID = '686823449348-u5bvf5bnfka4n6gmg28k0jb93d8uqq0r.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'
GOOGLE_REDIRECT_URI = 'http://localhost:5000/google/callback'
GOOGLE_SCOPE = 'https://www.googleapis.com/auth/userinfo.profile'

@app.route('/google')
def logingoogle():
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}&scope={GOOGLE_SCOPE}"
    )
    return redirect(auth_url)

@app.route('/google/callback')
def google_callback():
    code = request.args.get('code')
    if not code:
        google_login_result.put(None)
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
        google_login_result.put(None)
        return "Error al obtener el token.", 400

    user_info = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if user_info.status_code == 200:
        name = user_info.json().get("name", "Usuario")
        google_login_result.put(name)
    else:
        google_login_result.put(None)
        return "Error al obtener datos del perfil.", 400

    return "Inicio de sesión exitoso. Puedes cerrar esta pestaña."

def run_flask():
    app.run(port=5000)

# Ventanas

# Ventana principal
ventana_principal = tk.Tk()
ventana_principal.title("Sistema de Usuarios")
ventana_principal.geometry("1200x800")

frame_inicio = tk.Frame(ventana_principal)
frame_inicio.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(frame_inicio, text="Bienvenido", font=("Arial", 36)).pack(pady=40)
tk.Button(frame_inicio, text="Iniciar sesión", font=("Arial", 20), width=25, command=lambda: abrir_login()).pack(pady=20)
tk.Button(frame_inicio, text="Registrarse", font=("Arial", 20), width=25, command=lambda: abrir_registro()).pack(pady=20)

# Ventana de login
def abrir_login():
    global ventana_login, entry_usuario_login, entry_contraseña_login
    ventana_login = tk.Toplevel()
    ventana_login.title("Iniciar sesión")
    ventana_login.geometry("1200x800")

    frame_login = tk.Frame(ventana_login)
    frame_login.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame_login, text="Usuario", font=("Arial", 20)).pack(pady=10)
    entry_usuario_login = tk.Entry(frame_login, font=("Arial", 18), width=30)
    entry_usuario_login.pack(pady=10)

    tk.Label(frame_login, text="Contraseña", font=("Arial", 20)).pack(pady=10)
    entry_contraseña_login = tk.Entry(frame_login, show="*", font=("Arial", 18), width=30)
    entry_contraseña_login.pack(pady=10)

    tk.Button(frame_login, text="Iniciar con Facebook", font=("Arial", 16), bg="#3b5998", fg="white", width=25, command=iniciar_facebook).pack(pady=10)
    tk.Button(frame_login, text="Iniciar con Google", font=("Arial", 16), bg="#db4a39", fg="white", width=25, command=iniciar_google).pack(pady=10)

    tk.Button(frame_login, text="Entrar", font=("Arial", 20), width=20, command=iniciar_sesion).pack(pady=30)

# Ventana de registro
def abrir_registro():
    global ventana_registro, entry_usuario_registro, entry_contraseña_registro
    ventana_registro = tk.Toplevel()
    ventana_registro.title("Registro de usuario")
    ventana_registro.geometry("1200x800")

    frame_registro = tk.Frame(ventana_registro)
    frame_registro.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame_registro, text="Nuevo usuario", font=("Arial", 20)).pack(pady=10)
    entry_usuario_registro = tk.Entry(frame_registro, font=("Arial", 18), width=30)
    entry_usuario_registro.pack(pady=10)

    tk.Label(frame_registro, text="Nueva contraseña", font=("Arial", 20)).pack(pady=10)
    entry_contraseña_registro = tk.Entry(frame_registro, show="*", font=("Arial", 18), width=30)
    entry_contraseña_registro.pack(pady=10)

    tk.Button(frame_registro, text="Registrar", font=("Arial", 20), width=20, command=registrar_usuario).pack(pady=30)

#esto la incia (importante xd)
ventana_principal.mainloop()