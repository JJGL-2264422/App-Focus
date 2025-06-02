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
        self.configure(bg='#ED9119')
        self.usuario = usuario
        tk.Label(self, text=f"¡Bienvenido, {usuario}!",bg="#ED7819", fg="#FFFFFF",font=(tkFont.Font(family='Lexend',size='20',weight="bold")),height=2).pack(side='top',fill='x')

        main_frame = tk.Frame(self, bg='#ED9119')
        main_frame.pack(pady=10,side='top',fill='x')
        
        main_frame.grid_rowconfigure(0,weight=1)
        main_frame.grid_columnconfigure(0,weight=1)
        main_frame.grid_columnconfigure(1,weight=1)

        btn_crear = tk.Button(main_frame, text="Crear tarea", command= lambda: self.show_frame("FrameCrear"), width=20, height=2)
        btn_crear.grid(row=0,column=0)

        btn_ver = tk.Button(main_frame, text="Ver tareas", command= lambda: self.show_frame("FrameLista"), width=20, height=2)
        btn_ver.grid(row=0,column=1)


        contain = tk.Frame(self, bg='#FAF5F0')
        contain.pack(pady=10,padx=10,side = "top", fill = "both", expand = True) 

        switch_frame = tk.Frame(contain,bg='#FAF5F0')
        switch_frame.pack(padx=10,side = "top", fill = "both", expand = True) 
        switch_frame.grid_rowconfigure(0, weight = 1)
        switch_frame.grid_columnconfigure(0, weight = 1)
        
        self.frames = {}

        frame_lista = FrameLista(switch_frame, self)
        frame_crear = FrameCrear(switch_frame, self, frame_lista)

        self.frames["FrameCrear"] = frame_crear
        self.frames["FrameLista"] = frame_lista

        for frame in (self.frames.values()):
            frame.grid(row = 0, column = 0, sticky ="nswe")
        
        self.show_frame("FrameCrear")
    
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

# Crear tarea con input
class FrameCrear(tk.Frame):
    def __init__(self,parent,controller,frame_lista):
        tk.Frame.__init__(self,parent, bg='#FAF5F0')
        self.frame_lista = frame_lista

        main_frame = tk.Frame(self, bg='#FAF5F0')
        main_frame.pack(pady=20,side='top',fill='both')
        
        main_frame.grid_rowconfigure(0,weight=1)
        main_frame.grid_columnconfigure(0,weight=1)
        main_frame.grid_columnconfigure(1,weight=2)

        input_frame = tk.Frame(main_frame,bg='#FAF5F0')
        input_frame.grid(row=0,column=0,sticky='nse',padx=70)

        lista_frame = tk.Frame(main_frame,bg='#FAF5F0')
        lista_frame.grid_rowconfigure(0,weight=1)
        lista_frame.grid_columnconfigure(0,weight=1)
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

        columnas = ("Nombre","Fecha","Programa")
        self.tree = ttk.Treeview(lista_frame, columns=columnas, show="headings", height=16)
        
        try:
            tareas = requests.get("http://localhost:5000/Tareas")
            tareas = tareas.json()

            for col in columnas:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=150, anchor="center")

            for tarea in tareas:
                self.tree.insert("", "end", values=(tarea['nombre'],tarea['fecha'], tarea['programa']))
        except Exception as e:
            print("Error:", e)

        self.tree.grid(row=0,column=0,sticky='w')
        scroll = ttk.Scrollbar(lista_frame,orient="vertical", command=self.tree.yview)
        scroll.grid(row=0,column=0,sticky='sne')

# Guardar tarea con fecha y hora actual
    def guardar_tarea(self,nombre, horaObj, programa):
        if not nombre and not horaObj and not programa:
            messagebox.showinfo("Datos Faltantes", f"Por favor, rellene el formulario.")
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
    
    def actualizar_lista(self): # Actualiza su propia tabla y la tabla de FrameLista
        for item in self.tree.get_children():
            self.tree.delete(item)

        tareas = requests.get("http://localhost:5000/Tareas")
        tareas = tareas.json()

        for tarea in tareas:
            self.tree.insert("", "end", values=(tarea['nombre'],tarea['fecha'], tarea['programa']))
        
        self.frame_lista.actualizar_ext(tareas)
        self.update()

# Mostrar ventana con tabla de tareas

class FrameLista(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent, bg='#FAF5F0')
        self.controller = controller
        frame_tabla = tk.Frame(self,bg='#FAF5F0')
        frame_tabla.pack(pady=15)

        columnas = ("Nombre", "Fecha", "Hora","Horas de Trabajo","Programa")
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=12)
        

        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        tareas = requests.get("http://localhost:5000/Tareas")
        tareas = tareas.json()

        for tarea in tareas:
            self.tree.insert("", "end", values=(tarea['nombre'], tarea['fecha'], tarea['hora'], tarea['horaObj'], tarea['programa']))

        self.tree.pack(side='left')
        
        scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        scroll.pack(side='right', fill='y')
                
        btn_iniciar = tk.Button(self, text="Iniciar tarea", font=(tkFont.Font(family='Lexend',size='10',weight='bold') ), width=16, command= lambda: self.iniciar_tarea(tareas),height=1)
        btn_iniciar.pack()
        tk.Label(self, text="(Seleccione una tarea para iniciar el cronometro)", font=(tkFont.Font(family='Lexend',size='8') ),bg='#FAF5F0').pack(pady=15)
        

    def actualizar_ext(self, datos): #Actualiza la tabla desde FrameCrear o desde sí mismo.
        for item in self.tree.get_children():
            self.tree.delete(item)

        for tarea in datos:
            self.tree.insert("", "end", values=(tarea['nombre'], tarea['fecha'], tarea['hora'], tarea['horaObj'], tarea['programa']))
    
    def iniciar_tarea(self, datos):
        try:
            nom_tarea = self.tree.item(self.tree.focus()).get("values")[0]
            prom_tarea = self.tree.item(self.tree.focus()).get("values")[4]
        except Exception as e:
            messagebox.showerror("Error", f"Selección no válida: {e}")
            return

        tarea = next((t for t in datos if t["nombre"] == nom_tarea and t["programa"] == prom_tarea), None)

        if not tarea:
            messagebox.showerror("Error", "Tarea no encontrada")
            return

        entrada = {
            "programa": tarea["programa"],
            "nombre": tarea["nombre"]
        }

        with open("Entrada.json", "w") as f:
            json.dump(entrada, f)
        
        self.controller.withdraw()
        
        subprocess.run(["myvenv/Scripts/python", "cronometro.py"])

        self.controller.deiconify()
        
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

        for t in datos:
            if t["nombre"] == nom_tarea:
                t["horaObj"] = f"{horas_final:02}:{minutos_final:02}:{segundos_final:02}"
                break

        r = requests.put("http://localhost:5000/Tareas", json=datos)

        self.actualizar_ext(datos)

        messagebox.showinfo("Cerrado","Cronómetro finalizado")


