#utils2.py
import os
def error1():
    print("Elemento duplicado")
def error2():
    print("Elemento invalido")
def error3():
    print("El campo no puede estar vacio")
DATA_FOLDER = 'data'
def _ensure_data_folder(folder: str = DATA_FOLDER):
    os.makedirs(folder, exist_ok=True)

validate_types = ["comercial", "militar", "carga", "privado"]
airplane_vstatus = ["en_vuelo", "en_tierra", "despegando", "aterrizando", "esperando_pista"]
pilot_vstatus = ["descansando", "disponible", "ocupado"]
airstrip_vstatus = ["ocupada", "disponible", "en_reparacion"]
