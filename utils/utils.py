# utils.py
import os
import time
from models.airplane import add_airplane, save_airplanes_json, view_airplanes_list
from models.airstrip import add_airstrip, save_airstrips_json, view_airstrip_list
from models.pilot import add_pilot, save_pilots_json, view_pilot_list


def limpiar_pantalla():
    # En Windows suele ser 'cls'; si solo usas Linux/Mac, deja 'clear'
    os.system("cls" if os.name == "nt" else "clear")


# -------- AVIONES --------

def menu_gestion_aviones():
    print("======== GESTIÓN DE AERONAVES ========")
    print("\nOpciones:")
    print("1. Agregar avión")
    print("2. Ver aviones")
    print("3. Guardar aviones")
    print("4. Salir al menú principal")


def gestion_aviones():
    while True:
        limpiar_pantalla()
        menu_gestion_aviones()
        try:
            opcion = int(input("Seleccione una opción: "))
        except ValueError:
            print("Debe ingresar un número.")
            input("Presione Enter para continuar...")
            continue

        if opcion == 1:
            limpiar_pantalla()
            avion_id = input("ID del avión. No debe exceder los 6 símbolos: ").strip()
            tipo = input("Tipo de aeronave (CARGA, PRIVADO, MILITAR, COMERCIAL): ").strip()
            add_airplane(avion_id, tipo)
            save_airplanes_json()
            print("Avión agregado y guardado.")
            input("Presione Enter para continuar...")

        elif opcion == 2:
            limpiar_pantalla()
            view_airplanes_list()
            input("Presione Enter para continuar...")

        elif opcion == 3:
            limpiar_pantalla()
            print("Guardando....")
            time.sleep(2)
            save_airplanes_json()
            print("Guardado completo")
            input("Presione Enter para continuar...")

        elif opcion == 4:
            limpiar_pantalla()
            break

        else:
            print("Comando desconocido")
            input("Presione Enter para continuar...")


# -------- PILOTOS --------

def menu_gestion_pilotos():
    print("======== GESTIÓN DE PILOTOS ========")
    print("\nOpciones:")
    print("1. Agregar piloto")
    print("2. Ver pilotos")
    print("3. Guardar pilotos")
    print("4. Salir al menú principal")
    print("\n")


def gestion_pilotos():
    while True:
        limpiar_pantalla()
        menu_gestion_pilotos()
        try:
            opcion = int(input("Seleccione una opción: "))
        except ValueError:
            print("Debe ingresar un número.")
            input("Presione Enter para continuar...")
            continue

        if opcion == 1:
            limpiar_pantalla()
            ID = input("ID del piloto. No exceder los 6 símbolos: ").strip()
            nombre = input("Nombre del piloto: ").strip()
            apellido = input("Apellido del piloto: ").strip()
            tipo = input("Tipo de avión que vuela el piloto: ").strip()
            add_pilot(ID, nombre, apellido, tipo)
            save_pilots_json()
            print("Piloto agregado y guardado.")
            input("Presione Enter para continuar...")

        elif opcion == 2:
            limpiar_pantalla()
            view_pilot_list()
            input("Presione Enter para continuar...")

        elif opcion == 3:
            limpiar_pantalla()
            print("Guardando....")
            time.sleep(2)
            save_pilots_json()
            print("Guardado completo")
            input("Presione Enter para continuar...")

        elif opcion == 4:
            limpiar_pantalla()
            break

        else:
            print("Comando desconocido")
            input("Presione Enter para continuar...")


# -------- PISTAS --------

def menu_gestion_pistas():
    print("======== GESTIÓN DE PISTAS ========")
    print("\nOpciones:")
    print("1. Agregar pista")
    print("2. Ver pistas")
    print("3. Guardar pistas")
    print("4. Salir")
    print("\n")


def gestion_pistas():
    while True:
        limpiar_pantalla()
        menu_gestion_pistas()
        try:
            aux = int(input("Seleccione una opción: "))
        except ValueError:
            print("Debe ingresar un número.")
            input("Presione Enter para continuar...")
            continue

        if aux == 1:
            limpiar_pantalla()
            ID = input("ID de la pista. No debe exceder los 4 símbolos (ejemplo: P-01): ").strip()
            callsign = None  # si no ingresas uno, se usará el ID como callsign
            msg = add_airstrip(ID, callsign)
            save_airstrips_json()
            print(msg)
            input("Presione Enter para continuar...")

        elif aux == 2:
            limpiar_pantalla()
            view_airstrip_list()
            input("Presione Enter para continuar...")

        elif aux == 3:
            limpiar_pantalla()
            print("Guardando....")
            time.sleep(2)
            save_airstrips_json()
            print("Guardado completo")
            input("Presione Enter para continuar...")

        elif aux == 4:
            limpiar_pantalla()
            break

        else:
            print("Comando desconocido")
            input("Presione Enter para continuar...")
