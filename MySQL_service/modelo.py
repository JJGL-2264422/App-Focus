from sqlalchemy import String, Integer, Column, Date, Time

from basedatos import Base

class TareaSQL(Base):
    __tablename__="tareas"
    id_tarea = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    fecha = Column(Date)
    hora = Column(Time)
    horaObj = Column(Time)
    programa = Column(String(100))