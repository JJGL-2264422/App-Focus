import tkinter as tk
from tkinter import messagebox
import json
import os

#JSON
DATA_FILE = 'usuarios.json'
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

# Funciones

def mostrar_bienvenida(usuario):
    ventana_bienvenida = tk.Toplevel()
    ventana_bienvenida.title("Bienvenido")
    ventana_bienvenida.geometry("1200x800")

    frame = tk.Frame(ventana_bienvenida)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame, text=f"¡Bienvenido, {usuario}!", font=("Arial", 32)).pack(pady=40)
    tk.Button(frame, text="Cerrar sesión", font=("Arial", 18), width=20,
              command=lambda: cerrar_sesion(ventana_bienvenida)).pack(pady=20)

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
        ventana_principal.withdraw()
        mostrar_bienvenida(usuario)
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

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
