import time
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
import json
import os
from flask import Flask, request, redirect, render_template_string
import webbrowser
from queue import Queue
import api_gateway

import tarea

#JSON
DATA_FILE = 'usuarios.json'
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

# Funciones
def cerrar_sesion(ventana_actual):
    ventana_actual.destroy()
    ventana_principal.deiconify()

def registrar_usuario(user,password, repassword):
    usuario = user
    contraseña = password
    confir_contraseña = repassword

    if not usuario or not contraseña:
        messagebox.showwarning("Campos vacíos", "Por favor, completa todos los campos.")
        return

    if contraseña != confir_contraseña:
        messagebox.showwarning("Confirmar Contraseña", "Las contraseñas no concuerdan.")
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
    return

def iniciar_sesion(user, password):
    usuario = user
    contraseña = password

    with open(DATA_FILE, 'r') as f:
        usuarios = json.load(f)

    if usuario in usuarios and usuarios[usuario] == contraseña:
        ventana_principal.destroy()
        tarea.VentanaPrincipal(usuario)
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos.")


def login_facebook():
    webbrowser.open('http://localhost:5000/facebook')
    verificar_login()


def login_google():
    webbrowser.open('http://localhost:5000/google')
    verificar_login()

def verificar_login():
    while True:
        if os.path.exists("info_usuario.json"):
            try:
                with open("info_usuario.json", "r") as f:
                    datos = json.load(f)
                    nombre = datos.get("nombre")

                if nombre:
                    os.remove("info_usuario.json")
                    ventana_principal.destroy()
                    tarea.VentanaPrincipal(nombre)
                    break

            except Exception as e:
                print("Error leyendo el nombre de usuario", e)

        time.sleep(1)
#Importante importar datetime para el time

# Ventanas

class VentanaPrincipal(tk.Tk):
    def __init__(self,*arg,**kwargs):
        tk.Tk.__init__(self, *arg,**kwargs)
        self.geometry("1000x600")
        main_frame = tk.Frame(self)
        main_frame.pack(side = "top", fill = "both", expand = True) 
        
        main_frame.grid_rowconfigure(0, weight = 1)
        main_frame.grid_columnconfigure(0, weight = 1)
        
        self.frames = {}

        for F in (VentanaLogin,VentanaRegistro):
 
            frame = F(main_frame, self)
 
            self.frames[F] = frame 
 
            frame.grid(row = 0, column = 0, sticky ="nsew")
        self.show_frame(VentanaLogin)
    
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


# Ventana principal / Inicio de sesión
class VentanaLogin(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
    
        frame_inicio = tk.Frame(self,bg='#FAF5F0')

        gradiente = tk.Canvas(self, bg="#ED4319")

        frame_formulario = tk.Frame(frame_inicio,bg='#FAF5F0')
        tk.Label(frame_formulario, text="Iniciar Sesión", font=(tkFont.Font(family='Lexend',size='26',weight='bold') ),bg='#FAF5F0').pack(pady=10,anchor='w')
        tk.Label(frame_formulario, text="Usuario", font=(tkFont.Font(family='Lexend',size='12') ),bg='#FAF5F0').pack(anchor='w')
        entry_usuario = tk.Entry(frame_formulario, font=("Arial", 10), width=20)
        entry_usuario.pack(fill='x',pady=15)

        tk.Label(frame_formulario, text="Contraseña", font=(tkFont.Font(family='Lexend',size='12') ),bg='#FAF5F0').pack(anchor='w')
        entry_contraseña = tk.Entry(frame_formulario, show="*", font=("Arial", 10), width=20)
        entry_contraseña.pack(fill='x',pady=5)


        tk.Button(frame_formulario, text="Iniciar con Facebook", font=(tkFont.Font(family='Lexend',size='10',weight='bold') ), bg="#0866FF", fg="white", width=25, command=login_facebook).pack(fill='x',pady=10)
        tk.Button(frame_formulario, text="Iniciar con Google", font=(tkFont.Font(family='Lexend',size='10',weight='bold') ), bg="#DD4722", fg="white", width=25, command=login_google).pack(fill='x',pady=10)

        tk.Button(frame_formulario, text="Iniciar sesión", font=(tkFont.Font(family='Lexend',size='10',weight='bold') ), width=12, command=lambda: iniciar_sesion(entry_usuario.get(),entry_contraseña.get())).pack(side='left',pady=20)
        tk.Button(frame_formulario, text="Registrarse", font=(tkFont.Font(family='Lexend',size='10',weight='bold') ), width=12, command=lambda: controller.show_frame(VentanaRegistro)).pack(side='right',pady=20)

        frame_formulario.pack(fill='x',expand='true')
        frame_formulario.place(relx=0.5, rely=0.5, anchor="center")

        gradiente.pack(side='left',fill='both', expand='true')
        frame_inicio.pack(side='right',fill='both',expand='true')
        self.pack(fill='both',expand='true')


class VentanaRegistro(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent, bg='#ED4319')
        frame_registro = tk.Frame(self,width=400,bg='#FAF5F0')
        frame_registro.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame_registro, text="",bg='#FAF5F0', font=("Arial", 10)).pack()
        tk.Label(frame_registro, text="Registro", font=(tkFont.Font(family='Lexend',size='24',weight='bold') ),bg='#FAF5F0').pack(pady=15,anchor='center')
        tk.Label(frame_registro, text="Usuario",bg='#FAF5F0', font=(tkFont.Font(family='Lexend',size='12') )).pack()
        entry_usuario = tk.Entry(frame_registro, font=("Arial", 10), width=30)
        entry_usuario.pack(pady=10,padx=40)

        tk.Label(frame_registro, text="Contraseña",bg='#FAF5F0', font=(tkFont.Font(family='Lexend',size='12') )).pack()
        entry_contraseña = tk.Entry(frame_registro, show="*", font=("Arial", 10), width=30)
        entry_contraseña.pack(pady=10,padx=40)

        tk.Label(frame_registro, text="Confirmar contraseña",bg='#FAF5F0', font=(tkFont.Font(family='Lexend',size='12') )).pack()
        entry_confir_contraseña = tk.Entry(frame_registro, show="*", font=("Arial", 10), width=30)
        entry_confir_contraseña.pack(pady=10,padx=40)

        tk.Button(frame_registro, text="Registrarse", font=(tkFont.Font(family='Lexend',size='10',weight='bold')), width=14, command= lambda: [registrar_usuario(entry_usuario.get(),entry_contraseña.get(),entry_confir_contraseña.get()),controller.show_frame(VentanaLogin)] ).pack(pady=10)
        tk.Button(frame_registro, text="Volver", font=(tkFont.Font(family='Lexend',size='10',weight='bold')), width=12, command= lambda: controller.show_frame(VentanaLogin) ).pack(pady=15)

#esto la incia (importante xd)
ventana_principal = VentanaPrincipal()
ventana_principal.mainloop()