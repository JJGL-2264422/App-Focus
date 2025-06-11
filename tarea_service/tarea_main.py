from fastapi import FastAPI, Depends, HTTPException, Header
from jose import jwt, JWTError
from pydantic import BaseModel
import json
import os
import unicodedata

app = FastAPI()

SECRET_KEY = "clave-secreta"
ALGORITHM = "HS256"

BASE_DIR = os.path.dirname(__file__)
COMMON_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "common"))
TAREAS_FILE = os.path.join(COMMON_DIR, "tareas.json")
SALIDA_FILE = os.path.join(COMMON_DIR, "salida.json")

class Tarea(BaseModel):
    nombre: str
    fecha: str
    hora: str
    horaObj: str
    programa: str

class Tiempo(BaseModel):
    nombre: str
    tiempo: str

def verify_token(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except (JWTError, IndexError):
        raise HTTPException(status_code=401, detail="Token inválido")

def hhmmss_a_segundos(hhmmss: str) -> int:
    h, m, s = map(int, hhmmss.strip().split(":"))
    return h * 3600 + m * 60 + s

def segundos_a_hhmmss(segundos: int) -> str:
    h = segundos // 3600
    m = (segundos % 3600) // 60
    s = segundos % 60
    return f"{h:02}:{m:02}:{s:02}"

@app.get("/tareas")
def get_tareas(user: str = Depends(verify_token)):
    if not os.path.exists(TAREAS_FILE):
        return []
    with open(TAREAS_FILE, "r") as f:
        return json.load(f)

@app.post("/tareas")
def add_tarea(tarea: Tarea, user: str = Depends(verify_token)):
    tareas = []
    if os.path.exists(TAREAS_FILE):
        with open(TAREAS_FILE, "r") as f:
            tareas = json.load(f)
    tareas.append(tarea.dict())
    with open(TAREAS_FILE, "w") as f:
        json.dump(tareas, f, indent=4)
    return {"mensaje": "Tarea guardada"}

@app.put("/tareas")
def update_tareas(tareas: list[Tarea], user: str = Depends(verify_token)):
    with open(TAREAS_FILE, "w") as f:
        json.dump([t.dict() for t in tareas], f, indent=4)
    return {"mensaje": "Tareas actualizadas"}

@app.post("/tiempo")
def guardar_tiempo(t: Tiempo):
    if not os.path.exists(TAREAS_FILE):
        return {"mensaje": "Archivo tareas.json no encontrado"}

    with open(TAREAS_FILE, "r") as f:
        tareas = json.load(f)

    nombre_recibido = t.nombre.strip().lower()
    actualizado = False

    for tarea in tareas:
        nombre_tarea = tarea.get("nombre", "").strip().lower()
        if nombre_tarea == nombre_recibido:
            try:
                tiempo_anterior = hhmmss_a_segundos(tarea.get("horaObj", "00:00:00"))
                tiempo_nuevo = hhmmss_a_segundos(t.tiempo)
                tiempo_restante = max(0, tiempo_anterior - tiempo_nuevo)
                tarea["horaObj"] = segundos_a_hhmmss(tiempo_restante)
                actualizado = True
            except Exception as e:
                return {"mensaje": f"Error al calcular tiempo restante: {e}"}
            break

    with open(SALIDA_FILE, "w") as f:
        json.dump(t.dict(), f)

    if actualizado:
        with open(TAREAS_FILE, "w") as f:
            json.dump(tareas, f, indent=4)
        return {"mensaje": "Tiempo guardado y tarea actualizada"}
    else:
        return {"mensaje": f"No se encontró la tarea con nombre '{t.nombre}'"}
