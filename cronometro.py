import psutil
import tkinter as tk
import win32gui as wui
import win32process as winp
import json
import requests
import os
import sys


BASE_DIR = os.path.dirname(__file__)
COMMON_DIR = os.path.abspath(os.path.join(BASE_DIR, "common"))
ENTRADA_FILE = os.path.join(COMMON_DIR, "Entrada.json")
SALIDA_FILE = os.path.join(COMMON_DIR, "salida.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.jwt")

API_URL = "http://localhost:8000"
active = True

try:
    with open(ENTRADA_FILE, "r") as f:
        datos = json.load(f)
        programas = [datos.get("programa", [])]
        nombre = datos.get("nombre", "")
except Exception as e:
    print("Error al leer Entrada.json:", e)
    programas = []
    nombre = ""

#Código de Ventana Arrastrable creado por James Kent
class Grip:
    def __init__ (self, parent, disable=None, releasecmd=None) :
        self.parent = parent
        self.root = parent.winfo_toplevel()

        self.disable = disable
        if type(disable) == 'str':
            self.disable = disable.lower()

        self.releaseCMD = releasecmd

        self.parent.bind('<Button-1>', self.relative_position)
        self.parent.bind('<ButtonRelease-1>', self.drag_unbind)

    def relative_position (self, event) :
        cx, cy = self.parent.winfo_pointerxy()
        geo = self.root.geometry().split("+")
        self.oriX, self.oriY = int(geo[1]), int(geo[2])
        self.relX = cx - self.oriX
        self.relY = cy - self.oriY

        self.parent.bind('<Motion>', self.drag_wid)

    def drag_wid (self, event) :
        cx, cy = self.parent.winfo_pointerxy()
        d = self.disable
        x = cx - self.relX
        y = cy - self.relY
        if d == 'x' :
            x = self.oriX
        elif d == 'y' :
            y = self.oriY
        self.root.geometry('+%i+%i' % (x, y))

    def drag_unbind (self, event) :
        self.parent.unbind('<Motion>')
        if self.releaseCMD != None :
            self.releaseCMD()


def update():
    global startTime, winCode, timer, AppName, ScoreL
    working = False
    winCode = winp.GetWindowThreadProcessId(wui.GetForegroundWindow()) #Toma el código de la aplicación activa
    try:
        winName = psutil.Process(winCode[-1]).name() #Toma el nombre de la aplicación a partir del código
        for i in range(0,len(programas)):
            if winName == programas[i]:
                working = True

        AppName.configure(text=f"AppCode: {winName}") #Debug
        if(working):
            startTime += 1
            seconds = startTime % 60
            minutes = int(startTime / 60) % 60
            hours = int(startTime / 3600)
            ScoreL.configure(text=f"{hours:02}:{minutes:02}:{seconds:02}",bg='lightgreen') #Cambia el color a verde mientras está activo
        else: #Cambia el color del fondo a rojo si está inactivo
            ScoreL.configure(bg='#f54257')
        timer.after(1000, update)
    except:
        winCode = winName = ""
        timer.after(5,update)

def openTimer():
    global startTime, winCode, timer, AppName, ScoreL, active
    timer = tk.Tk()
    winCode = 0
    startTime = 0
    seconds = startTime % 60
    minutes = int(startTime / 60) % 60
    hours = int(startTime / 3600)

    timer.title('-')
    timer.wm_attributes("-topmost", True)
    #timer.configure(bg='#f54257')

    AppName = tk.Label(timer, text=f"App Code: {winCode}") #Debug - Solo para mostrar el código de la aplicación activa
    AppName.pack()
    ScoreL = tk.Label(timer, text=f"{hours:02}:{minutes:02}:{seconds:02}", font=('Lexend',20), bg='#f54257')
    ScoreL.pack()

    timer.overrideredirect(True)
    grip = Grip(timer) #Hace arrastable la ventana del cronometro.

    timer.after(1000, update)
    timer.bind("<Escape>", lambda e: [close(), timer.destroy()])
    timer.mainloop()

def close():
    global nombre, startTime

    Time = startTime
    hours = int(Time / 3600)
    minutes = int(Time / 60) % 60
    seconds = Time % 60
    tiempo = f"{hours:02}:{minutes:02}:{seconds:02}"

    salida = {
        "nombre": nombre.strip(),
        "tiempo": tiempo
    }

    BASE_DIR = os.path.dirname(__file__)
    COMMON_DIR = os.path.abspath(os.path.join(BASE_DIR, "common"))
    SALIDA_FILE = os.path.join(COMMON_DIR, "salida.json")

    try:
        with open(SALIDA_FILE, "w") as f:
            json.dump(salida, f)
    except Exception as e:
        print(f"No se pudo escribir salida.json: {e}")

openTimer()
# [!] Solo es necesario cambiar el color del label del tiempo, ya que abarca toda la ventana.