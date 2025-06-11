import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import tkinter.font as tkFont
import json
import os
import subprocess
from datetime import datetime
import requests
import sys

COMMON_DIR = os.path.join(os.path.dirname(__file__), "common")
TAREAS_URL = "http://localhost:8000/Tareas"
SAVE_TIME_URL = "http://localhost:8000/SaveTime"
TOKEN_FILE = os.path.join(COMMON_DIR, "token.jwt")

def get_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None

class VentanaPrincipal(tk.Tk):
    def __init__(self, usuario, *arg, **kwargs):
        tk.Tk.__init__(self, *arg, **kwargs)
        self.geometry("1200x600")
        self.configure(bg='#ED9119')
        self.usuario = usuario
        tk.Label(self, text=f"¡Bienvenido, {usuario}!", bg="#ED7819", fg="#FFFFFF",
                 font=(tkFont.Font(family='Lexend', size=20, weight="bold")), height=2).pack(side='top', fill='x')

        main_frame = tk.Frame(self, bg='#ED9119')
        main_frame.pack(pady=10, side='top', fill='x')
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        btn_crear = tk.Button(main_frame, text="Crear tarea", command=lambda: self.show_frame("FrameCrear"),
                               width=20, height=2)
        btn_crear.grid(row=0, column=0)
        btn_ver = tk.Button(main_frame, text="Ver tareas", command=lambda: self.show_frame("FrameLista"),
                            width=20, height=2)
        btn_ver.grid(row=0, column=1)

        contain = tk.Frame(self, bg='#FAF5F0')
        contain.pack(pady=10, padx=10, side="top", fill="both", expand=True)
        switch_frame = tk.Frame(contain, bg='#FAF5F0')
        switch_frame.pack(padx=10, side="top", fill="both", expand=True)
        switch_frame.grid_rowconfigure(0, weight=1)
        switch_frame.grid_columnconfigure(0, weight=1)

        self.frames = {}
        frame_lista = FrameLista(switch_frame, self)
        frame_crear = FrameCrear(switch_frame, self, frame_lista)
        self.frames["FrameCrear"] = frame_crear
        self.frames["FrameLista"] = frame_lista

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nswe")
        self.show_frame("FrameCrear")
    
    def show_frame(self, cont):
        self.frames[cont].tkraise()

class FrameCrear(tk.Frame):
    def __init__(self, parent, controller, frame_lista):
        tk.Frame.__init__(self, parent, bg='#FAF5F0')
        self.frame_lista = frame_lista
        self.controller = controller
        main_frame = tk.Frame(self, bg='#FAF5F0')
        main_frame.pack(pady=20, side='top', fill='both')
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=2)
        input_frame = tk.Frame(main_frame, bg='#FAF5F0')
        input_frame.grid(row=0, column=0, sticky='nse', padx=70)
        lista_frame = tk.Frame(main_frame, bg='#FAF5F0')
        tk.Label(input_frame, text="Nombre de la Tarea", bg='#FAF5F0').pack()
        entry_nombre = tk.Entry(input_frame, width=40)
        entry_nombre.pack(pady=10)
        tk.Label(input_frame, text="Horas a trabajar (HH:MM:SS)", bg='#FAF5F0').pack()
        entry_horas = tk.Entry(input_frame, width=40)
        entry_horas.pack(pady=10)
        tk.Label(input_frame, text="Programa a utilizar", bg='#FAF5F0').pack()
        entry_program = tk.Entry(input_frame, width=40)
        entry_program.pack(pady=10)
        
        def guardar_tarea():
            nombre = entry_nombre.get()
            horaObj = entry_horas.get()
            programa = entry_program.get() + ".exe"
            if not nombre or not horaObj or not programa:
                messagebox.showwarning("Faltan datos", "Completa todos los campos.")
                return
            ahora = datetime.now()
            tarea = {
                "nombre": nombre,
                "fecha": ahora.strftime("%Y-%m-%d"),
                "hora": ahora.strftime("%H:%M:%S"),
                "horaObj": horaObj,
                "programa": programa
            }
            headers = {"Authorization": f"Bearer {get_token()}"}
            r = requests.post(TAREAS_URL, json=tarea, headers=headers)
            if r.ok:
                self.actualizar_tabla()
                self.frame_lista.actualizar_ext()
                messagebox.showinfo("Éxito", "Tarea guardada correctamente")
            else:
                messagebox.showerror("Error", f"No se pudo guardar la tarea.{r.json()}")
        tk.Button(input_frame, text="Crear Tarea", command=guardar_tarea).pack(pady=10)
    
        tabla_frame = tk.Frame(main_frame, bg='#FAF5F0')
        tabla_frame.grid(row=0, column=1, sticky='nswe')

        columnas = ("Nombre", "Fecha", "Hora", "Horas de Trabajo", "Programa")
        self.tree = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=12)
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")
        self.tree.pack(side='left', fill='both', expand=True)
        ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tree.yview).pack(side='right', fill='y')

        self.actualizar_tabla()

    def actualizar_tabla(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)

            headers = {"Authorization": f"Bearer {get_token()}"}
            r = requests.get(TAREAS_URL, headers=headers)
            tareas = r.json()

            for tarea in tareas:
                self.tree.insert("", "end", values=(tarea['nombre'], tarea['fecha'], tarea['hora'], tarea['horaObj'], tarea['programa']))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las tareas: {e}")

class FrameLista(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='#FAF5F0')
        self.controller = controller
        frame_tabla = tk.Frame(self, bg='#FAF5F0')
        frame_tabla.pack(pady=15)
        columnas = ("Nombre", "Fecha", "Hora", "Horas de Trabajo", "Programa")
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=12)
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(side='left')
        ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview).pack(side='right', fill='y')
        tk.Button(self, text="Iniciar tarea", command=self.iniciar_tarea).pack(pady=5)
        self.actualizar_ext()

    def actualizar_ext(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        headers = {"Authorization": f"Bearer {get_token()}"}
        r = requests.get(TAREAS_URL, headers=headers)
        tareas = r.json()
        for tarea in tareas:
            self.tree.insert("", "end", values=(tarea['nombre'], tarea['fecha'], tarea['hora'], tarea['horaObj'], tarea['programa']))

    def iniciar_tarea(self):
        try:
            import os
            import json
            import sys
            import subprocess
            import time

            BASE_DIR = os.path.dirname(__file__)
            COMMON_DIR = os.path.abspath(os.path.join(BASE_DIR, "common"))
            ENTRADA_FILE = os.path.join(COMMON_DIR, "Entrada.json")
            SALIDA_FILE = os.path.join(COMMON_DIR, "salida.json")

            item = self.tree.focus()
            if not item:
                messagebox.showwarning("Seleccionar tarea", "Por favor, selecciona una tarea.")
                return

            valores = self.tree.item(item)['values']
            entrada = {"nombre": valores[0], "programa": valores[4]}

            with open(ENTRADA_FILE, "w") as f:
                json.dump(entrada, f)

            self.controller.withdraw()
            subprocess.run([sys.executable, "cronometro.py"])

            if os.path.exists(SALIDA_FILE):
                with open(SALIDA_FILE, "r") as f:
                    salida = json.load(f)

                data = {
                    "nombre": salida["nombre"],
                    "tiempo": salida["tiempo"]
                }

                headers = {"Authorization": f"Bearer {get_token()}"} 
                response = requests.post(SAVE_TIME_URL, json=data, headers=headers)
                self.actualizar_ext()
                self.controller.frames["FrameCrear"].actualizar_tabla()

            else:
                messagebox.showwarning("Aviso", "No se encontró el archivo salida.json después de cerrar el cronómetro.")
            self.controller.deiconify()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar la tarea:\n{e}")