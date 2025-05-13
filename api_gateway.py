import json
import os
from tkinter import messagebox
from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class SaveTime(Resource):
    def post(self):
        time = request.json
        with open("salida.json", "w") as f:
            json.dump(time, f)

class Tareas(Resource):
    def get(self):
        if not os.path.exists("tareas.json"):
            messagebox.showinfo("Sin tareas", "No hay tareas guardadas")
            return

        with open("tareas.json", 'r') as f:
            tareas = json.load(f)
            return tareas

    def post(self):
        tarea = request.json
        if os.path.exists("tareas.json"):
            with open("tareas.json", 'r') as f:
                tareas = json.load(f)
        else:
            tareas = []

        tareas.append(tarea)

        with open("tareas.json", 'w') as f:
            json.dump(tareas, f, indent=6)
            
    def put(self):
        tareas = request.json
        with open("tareas.json", 'w') as f:
            json.dump(tareas, f,)


api.add_resource(SaveTime, "/SaveTime")
api.add_resource(Tareas,"/Tareas")

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5080,debug=True)