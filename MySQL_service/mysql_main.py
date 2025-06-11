from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Annotated
import modelo
from basedatos import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

class Tarea(BaseModel):
    nombre: str
    fecha: str
    hora: str
    horaObj: str
    programa: str

def get_bd():
    bd=SessionLocal()
    try:
        yield bd
    finally:
        bd.close()

bd_dependency = Annotated[Session, Depends(get_bd)]

@app.post("/registro", status_code=status.HTTP_201_CREATED)
async def crear_tarea(registro:Tarea, bd:bd_dependency):
    bd_tarea = modelo.TareaSQL(**registro.dict())
    bd.add(bd_tarea)
    bd.commit()
    return "Se añadió la tarea exitosamente"

@app.get("/listar", status_code=status.HTTP_200_OK)
async def consultar_tareas(bd:bd_dependency):
    tareas = bd.query(modelo.TareaSQL).all()
    return tareas

'''@app.get("/consultar/{dueño_tarea}", status_code=status.HTTP_200_OK) #No se utiliza por el momento
async def consultar_tareas_por_dueño(dueño_tarea, bd:bd_dependency):
    tarea = bd.query(modelo.TareaSQL).filter(modelo.TareaSQL.dueño_tarea==dueño_tarea).first()
    if tarea is None:
        HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea'''

@app.delete("/borrar/{id_tarea}", status_code=status.HTTP_200_OK)
async def borrar_registro(id_tarea, bd:bd_dependency):
    registroborrar = bd.query(modelo.TareaSQL).filter(modelo.TareaSQL.id_tarea==id_tarea).first()
    if registroborrar is None:
        HTTPException(status_code=404, detail="No se puede borrar o no existe la tarea")
    bd.delete(registroborrar)
    bd.commit()
    return "La tarea se elimino exitosamente"

@app.post("/actualizarHora", status_code=status.HTTP_200_OK)
async def actualizar_hora (horaObj, bd:bd_dependency):
     registroactualizar = bd.query(modelo.TareaSQL).filter(modelo.TareaSQL.id_tarea==horaObj).first()
     if registroactualizar is None:
         HTTPException(status_code=404, detail="No se encuentra la tarea")
     registroactualizar.horaObj = horaObj
     bd.commit()
     return "Tarea actualizada exitosamente"