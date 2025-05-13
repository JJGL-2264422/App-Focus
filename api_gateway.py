import json
from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class SaveTime(Resource):
    def post(self):
        time = request.json
        with open("salida.json", "w") as f:
            json.dump(time, f)

api.add_resource(SaveTime, "/SaveTime")

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5080,debug=True)