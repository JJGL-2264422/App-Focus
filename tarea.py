import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import json
import os
import subprocess
from datetime import datetime
import requests

#import login

TAREAS_FILE = 'tareas.json'

# Ventana principal
def dashboard(usuario):
    global root 
    root = tk.Tk()
    root.title("Bienvenido")
    root.geometry("1200x800")

    frame = tk.Frame(root)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame, text=f"¡Bienvenido, {usuario}!", font=("Arial", 32),height=2).pack(pady=40)
    #tk.Button(frame, text="Cerrar sesión", font=("Arial", 18), width=20,
    #          command=lambda: login.cerrar_sesion(root)).pack(pady=20)

    btn_crear = tk.Button(frame, text="Crear tarea", command=crear_tarea, width=30, height=2)
    btn_crear.pack(pady=20)

    btn_ver = tk.Button(frame, text="Ver tareas", command=mostrar_tareas, width=30, height=2)
    btn_ver.pack(pady=20)

    btn_iniciar = tk.Button(frame, text="Iniciar tarea", command=iniciar_tarea, width=30, height=2)
    btn_iniciar.pack(pady=20)

    root.mainloop()

# Guardar tarea con fecha y hora actual
def guardar_tarea(nombre, horaObj, programa):
    if not nombre:
        return

    ahora = datetime.now()
    fecha = ahora.strftime("%Y-%m-%d")
    hora = ahora.strftime("%H:%M:%S")

    tarea = {
        "nombre": nombre,
        "fecha": fecha,
        "hora": hora,
        "horaObj": horaObj,
        "programa": programa
    }

    r = requests.post("http://localhost:5000/Tareas", json=tarea)

    messagebox.showinfo("Tarea guardada", f"Tarea '{nombre}' guardada exitosamente")

# Mostrar ventana con tabla de tareas
def mostrar_tareas():
    
    ventana_tareas = tk.Toplevel(root)
    ventana_tareas.title("Lista de tareas")
    ventana_tareas.geometry("1200x800")

    frame = tk.Frame(ventana_tareas)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    columnas = ("Nombre", "Fecha", "Hora","Horas de Trabajo","Programa")
    tree = ttk.Treeview(frame, columns=columnas, show="headings", height=20)
    
    tareas = requests.get("http://localhost:5000/Tareas")
    tareas = tareas.json()

    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=200, anchor="center")

    for tarea in tareas:
        tree.insert("", "end", values=(tarea['nombre'], tarea['fecha'], tarea['hora'], tarea['horaObj'], tarea['programa']))

    tree.pack()

def iniciar_tarea():

    tareas = requests.get("http://localhost:5000/Tareas")
    tareas = tareas.json()

    nombres = [t["nombre"] for t in tareas]
    seleccion = simpledialog.askstring("Iniciar tarea", f"Selecciona una tarea:\n{', '.join(nombres)}")

    tarea = next((t for t in tareas if t["nombre"] == seleccion), None)

    if not tarea:
        messagebox.showerror("Error", "Tarea no encontrada")
        return

    entrada = {
        "programa": tarea["programa"],
        "nombre": tarea["nombre"]
    }

    with open("Entrada.json", "w") as f:
        json.dump(entrada, f)

    root.withdraw()
    
    subprocess.run(["python", "cronometro.py"])

    root.deiconify()
    
    with open("salida.json", "r") as f:
        salida = json.load(f)

    tiemposalida = salida["tiempo"]
    horas, minutos, segundos = map(int, tiemposalida.split(":"))
    tiempo_total_salida = horas * 3600 + minutos * 60 + segundos

    horasObj, minutosObj, segundosObj = map(int, tarea["horaObj"].split(":"))
    tiempo_totalObj = horasObj * 3600 + minutosObj * 60 + segundosObj

    tiempo_final = tiempo_totalObj - tiempo_total_salida

    horas_final = tiempo_final // 3600
    minutos_final = (tiempo_final % 3600) // 60
    segundos_final = tiempo_final % 60

    for t in tareas:
        if t["nombre"] == seleccion:
            t["horaObj"] = f"{horas_final:02}:{minutos_final:02}:{segundos_final:02}"
            break

    r = requests.put("http://localhost:5000/Tareas", json=tareas)

    messagebox.showinfo("Cronómetro finalizado")

# Crear tarea con input
def crear_tarea():
    
    root.geometry("1200x800")
    nombre = simpledialog.askstring("Crear tarea", "Nombre de la tarea:")
    horas = simpledialog.askstring("Crear tarea", "Horas que se desean trabajar (HH:MM:SS):")
    programa = simpledialog.askstring("Crear tarea", "Programa a utilizar:")
    programa += ".exe"
    guardar_tarea(nombre, horas, programa)