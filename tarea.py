import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import tkinter.font as tkFont
import json
import os
import subprocess
from datetime import datetime
import requests

#import login

TAREAS_FILE = 'tareas.json'

# Ventana principal
class VentanaPrincipal(tk.Tk):
    def __init__(self,usuario,*arg,**kwargs):
        tk.Tk.__init__(self, *arg,**kwargs)
        self.geometry("1000x600")
        self.configure(bg='#FAF5F0')
        self.usuario = usuario
        tk.Label(self, text=f"¡Bienvenido, {usuario}!",bg="#ED9119", font=(tkFont.Font(family='Lexend',size='24')),height=2).pack(side='top',fill='x')

        main_frame = tk.Frame(self, bg='#FAF5F0')
        main_frame.pack(pady=20,side='top',fill='x')
        
        main_frame.grid_rowconfigure(0,weight=1)
        main_frame.grid_columnconfigure(0,weight=1)
        main_frame.grid_columnconfigure(1,weight=1)
        main_frame.grid_columnconfigure(2,weight=1)

        btn_crear = tk.Button(main_frame, text="Crear tarea", command= lambda: self.show_frame("FrameCrear"), width=20, height=2)
        btn_crear.grid(row=0,column=0,sticky='e')

        btn_ver = tk.Button(main_frame, text="Ver tareas", command= lambda: self.show_frame("FrameLista"), width=20, height=2)
        btn_ver.grid(row=0,column=1)

        btn_iniciar = tk.Button(main_frame, text="Iniciar tarea", command= lambda: iniciar_tarea(self), width=20, height=2)
        btn_iniciar.grid(row=0,column=2,sticky='w')


        contain = tk.Frame(self, bg='#FAF5F0')
        contain.pack(padx=10,side = "top", fill = "both", expand = True) 

        switch_frame = tk.Frame(contain,bg='#FAF5F0')
        switch_frame.pack(padx=10,side = "top", fill = "both", expand = True) 
        switch_frame.grid_rowconfigure(0, weight = 1)
        switch_frame.grid_columnconfigure(0, weight = 1)
        
        self.frames = {}

        frame_lista = FrameLista(switch_frame)
        frame_crear = FrameCrear(switch_frame, frame_lista)

        self.frames["FrameCrear"] = frame_crear
        self.frames["FrameLista"] = frame_lista

        for frame in (self.frames.values()):
            frame.grid(row = 0, column = 0, sticky ="nswe")
        
        self.show_frame("FrameCrear")
    
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

# Guardar tarea con fecha y hora actual


# Crear tarea con input
class FrameCrear(tk.Frame):
    def __init__(self,parent,frame_lista):
        tk.Frame.__init__(self,parent, bg='#FAF5F0')
        self.frame_lista = frame_lista

        main_frame = tk.Frame(self, bg='#FAF5F0')
        main_frame.pack(pady=20,side='top',fill='x')
        
        main_frame.grid_rowconfigure(0,weight=1)
        main_frame.grid_columnconfigure(0,weight=1)
        main_frame.grid_columnconfigure(1,weight=2)

        input_frame = tk.Frame(main_frame,bg='#FAF5F0')
        input_frame.grid(row=0,column=0,sticky='nse',padx=70)

        lista_frame = tk.Frame(main_frame,bg='#FAF5F0')
        lista_frame.grid(row=0,column=1,sticky='nswe')

        input_frame.grid_rowconfigure(0,weight=1)
        input_frame.grid_columnconfigure(0,weight=1)

        tk.Label(input_frame, text="Nombre de la Tarea", font=(tkFont.Font(family='Lexend',size='12') ),bg='#FAF5F0').pack()
        entry_nombre = tk.Entry(input_frame, font=("Arial", 10), width=40)
        entry_nombre.pack(pady=15)

        tk.Label(input_frame, text="Horas a trabajar (HH:MM:SS)", font=(tkFont.Font(family='Lexend',size='12') ),bg='#FAF5F0').pack()
        entry_horas = tk.Entry(input_frame, font=("Arial", 10), width=40)
        entry_horas.pack(pady=15)

        tk.Label(input_frame, text="Programa a utilizar", font=(tkFont.Font(family='Lexend',size='12') ),bg='#FAF5F0').pack()
        entry_program = tk.Entry(input_frame, font=("Arial", 10), width=40)
        entry_program.pack(pady=5)
        
        tk.Button(input_frame, text="Crear Tarea", font=(tkFont.Font(family='Lexend',size='10',weight='bold') ), width=12, command= lambda: self.guardar_tarea( entry_nombre.get(), entry_nombre.get(), entry_nombre.get() ) ).pack(pady=20)

        columnas = ("Nombre","Horas de Trabajo","Programa")
        self.tree = ttk.Treeview(lista_frame, columns=columnas, show="headings", height=20)
        
        try:
            tareas = requests.get("http://localhost:5000/Tareas")
            tareas = tareas.json()

            for col in columnas:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=150, anchor="center")

            for tarea in tareas:
                self.tree.insert("", "end", values=(tarea['nombre'],tarea['horaObj'], tarea['programa']))
        except Exception as e:
            print("Error:", e)

        self.tree.grid(row=0,column=0)

    def guardar_tarea(self,nombre, horaObj, programa):
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

        self.actualizar_lista()

        messagebox.showinfo("Tarea guardada", f"Tarea '{nombre}' guardada exitosamente")
    
    def actualizar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        tareas = requests.get("http://localhost:5000/Tareas")
        tareas = tareas.json()

        for tarea in tareas:
            self.tree.insert("", "end", values=(tarea['nombre'],tarea['horaObj'], tarea['programa']))
        
        self.frame_lista.actualizar_al_crear(tareas)
        self.update()

# Mostrar ventana con tabla de tareas

class FrameLista(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self,parent, bg='#FAF5F0')

        columnas = ("Nombre", "Fecha", "Hora","Horas de Trabajo","Programa")
        self.tree = ttk.Treeview(self, columns=columnas, show="headings", height=20)
        

        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        tareas = requests.get("http://localhost:5000/Tareas")
        tareas = tareas.json()

        for tarea in tareas:
            self.tree.insert("", "end", values=(tarea['nombre'], tarea['fecha'], tarea['hora'], tarea['horaObj'], tarea['programa']))

        self.tree.pack()

    def actualizar_al_crear(self, datos):
        for item in self.tree.get_children():
            self.tree.delete(item)


        for tarea in datos:
            self.tree.insert("", "end", values=(tarea['nombre'], tarea['fecha'], tarea['hora'], tarea['horaObj'], tarea['programa']))

class TreeUpdater():
    def __init__(self, treeview):
        print("Acá en el inicio")
        self.tree = treeview
        self.update_tree()
    
    def update_tree(self):
        print("Por aquí pasó")
        
    
# Falta interfaz gráfica
# No actualiza las listas de los frames
def iniciar_tarea(self):

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

    self.withdraw()
    
    subprocess.run(["myvenv/Scripts/python", "cronometro.py"])

    self.deiconify()
    
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
