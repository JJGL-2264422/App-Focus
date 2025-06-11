import subprocess
import time
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
procesos = []

print("Iniciando api_gateway en el puerto 8000...")
gateway_path = os.path.join(BASE_DIR, "api_gateway")
p_gateway = subprocess.Popen([
    "uvicorn", "gateway_main:app",
    "--port", "8000", "--reload"
], cwd=gateway_path)
procesos.append(p_gateway)
time.sleep(1)

print("Iniciando auth_service en el puerto 8001...")
auth_path = os.path.join(BASE_DIR, "auth_service")
p_auth = subprocess.Popen([
    "uvicorn", "auth_main:app",
    "--port", "8001", "--reload"
], cwd=auth_path)
procesos.append(p_auth)
time.sleep(1)

print("Iniciando tarea_service en el puerto 8002...")
tarea_path = os.path.join(BASE_DIR, "tarea_service")
p_tarea = subprocess.Popen([
    "uvicorn", "tarea_main:app",
    "--port", "8002", "--reload"
], cwd=tarea_path)
procesos.append(p_tarea)
time.sleep(1)

print("Iniciando oauth_service en el puerto 8003...")
oauth_path = os.path.join(BASE_DIR, "oauth_service")
p_oauth = subprocess.Popen([
    "uvicorn", "oauth_main:app",
    "--port", "8003", "--reload"
], cwd=oauth_path)
procesos.append(p_oauth)
time.sleep(1)

print("Iniciando MySQL_service en el puerto 8004...")
mysql_path = os.path.join(BASE_DIR, "MySQL_service")
p_mysql = subprocess.Popen([
    "uvicorn", "mysql_main:app",
    "--port", "8004", "--reload"
], cwd=mysql_path)
procesos.append(p_mysql)
time.sleep(1)

print("\nEsperando a que los servicios arranquen...")
time.sleep(3)

print("Iniciando la aplicación de escritorio...\n")
subprocess.run([sys.executable, os.path.join(BASE_DIR, "login.py")])

print("Cerrando microservicios...")
for proceso in procesos:
    proceso.terminate()
