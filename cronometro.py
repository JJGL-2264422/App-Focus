import tkinter as tk
import win32gui as wui

class Grip:
    ''' Makes a window dragable. '''
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
    winCode = wui.GetForegroundWindow() #Toma el código de la aplicación activa
    winTitle = wui.GetWindowText(wui.GetForegroundWindow()) #Debug - Toma el título de la ventana activa
    timer.title(winTitle)
    AppName.configure(text=f"AppCode: {winCode}")
    if(winCode == 788944):
        startTime += 1
        seconds = startTime % 60
        minutes = int(startTime / 60) % 60
        hours = int(startTime / 3600)
        ScoreL.configure(text=f"{hours:02}:{minutes:02}:{seconds:02}")
    timer.after(1000, update)

def main():
    global startTime, winCode, timer, AppName, ScoreL
    timer = tk.Tk()
    winCode = 0
    timer.title('-')
    timer.wm_attributes("-topmost", True)
    startTime = 0 #Se cambia por el valor guardado

    AppName = tk.Label(timer, text=f"App Code: {winCode}") #Debug - Solo para mostrar el código de la aplicación activa
    AppName.pack()
    ScoreL = tk.Label(timer, text="00:00:00", font=('Lexend',20))
    ScoreL.pack()

    timer.overrideredirect(True)
    grip = Grip(timer)

    timer.after(1000, update) # start the update 1 second later
    timer.mainloop()

main()