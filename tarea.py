import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import json
import os
from datetime import datetime

TAREAS_FILE = 'tareas.json'

# Guardar tarea con fecha y hora actual
def guardar_tarea(nombre):
    if not nombre:
        return

    ahora = datetime.now()
    fecha = ahora.strftime("%Y-%m-%d")
    hora = ahora.strftime("%H:%M:%S")

    tarea = {
        "nombre": nombre,
        "fecha": fecha,
        "hora": hora,
    }

    if os.path.exists(TAREAS_FILE):
        with open(TAREAS_FILE, 'r') as f:
            tareas = json.load(f)
    else:
        tareas = []

    tareas.append(tarea)

    with open(TAREAS_FILE, 'w') as f:
        json.dump(tareas, f, indent=4)

    messagebox.showinfo("Tarea guardada", f"Tarea '{nombre}' guardada exitosamente")

# Mostrar ventana con tabla de tareas
def mostrar_tareas():
    if not os.path.exists(TAREAS_FILE):
        messagebox.showinfo("Sin tareas", "No hay tareas guardadas")
        return

    with open(TAREAS_FILE, 'r') as f:
        tareas = json.load(f)

    ventana_tareas = tk.Toplevel(root)
    ventana_tareas.title("Lista de tareas")
    ventana_tareas.geometry("1200x800")

    frame = tk.Frame(ventana_tareas)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    columnas = ("Nombre", "Fecha", "Hora")
    tree = ttk.Treeview(frame, columns=columnas, show="headings", height=20)

    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=350, anchor="center")

    for tarea in tareas:
        tree.insert("", "end", values=(tarea['nombre'], tarea['fecha'], tarea['hora']))

    tree.pack()

# Crear tarea con input
def crear_tarea():
    
    root.geometry("1200x800")
    nombre = simpledialog.askstring("Crear tarea", "Nombre de la tarea:")
    guardar_tarea(nombre)

# Ventana principal
root = tk.Tk()
root.title("Gestor de tareas")
root.geometry("1200x800")

frame_principal = tk.Frame(root)
frame_principal.place(relx=0.5, rely=0.5, anchor="center")

btn_crear = tk.Button(frame_principal, text="Crear tarea", command=crear_tarea, width=30, height=2)
btn_crear.pack(pady=20)

btn_ver = tk.Button(frame_principal, text="Ver tareas", command=mostrar_tareas, width=30, height=2)
btn_ver.pack(pady=20)

root.mainloop()
