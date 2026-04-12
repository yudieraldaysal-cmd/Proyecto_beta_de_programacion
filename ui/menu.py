# menu.py
from models.events import (
create_event,
save_events_json,
view_events_list,
load_events_json,
simular_calendario,
simular_por_tiempo,
obtener_tiempo_actual,
establecer_tiempo_actual,
avanzar_tiempo,
reiniciar_tiempo,
mostrar_tiempo_actual,
simular_siguiente_evento,
delete_events_by_time,
delete_event_by_id)
from models.airplane import (
load_airplanes_json,
view_airplanes_list,
airplanes_map, save_airplanes_json,
marcar_avion_mantenimiento,
marcar_avion_ocupado,
avion_ocupado,
tipo_avion)
from models.airstrip import (
load_airstrips_json,
view_airstrip_list,
save_airstrips_json,
marcar_pista_mantenimiento,
marcar_pista_ocupada,
pista_ocupada)
from models.pilot import (
load_pilots_json,
pilots_map,
view_pilot_list,
save_pilots_json,
marcar_piloto_ocupado,
piloto_ocupado,
tipo_piloto)
from utils.utils import limpiar_pantalla, gestion_aviones, gestion_pilotos, gestion_pistas
import time

load_airplanes_json()
load_pilots_json()
load_events_json()
load_airstrips_json()



def main_menu():
    print("======== TORRE DE CONTROL - MENU PRINCIPAL ========")
    print(mostrar_tiempo_actual())
    print("\n\nOpciones:")
    print("1. Avanzar el tiempo")
    print("2. Establecer tiempo especifico")
    print("3. Agregar evento")
    print("4. Gestionar aviones")
    print("5. Gestionar pilotos")
    print("6. Gestionar pistas")
    print("7. Ver eventos")
    print("8. Simular siguiente evento")
    print("9. Simular varios eventos")
    print("10. Simular calendario por tiempo")
    print("11. Simular calendario completo")
    print("12. Reiniciar el tiempo a 0")
    print("13. Salir")
    print("\n")


def main():
    while True:
        limpiar_pantalla()
        main_menu()
        try:
            opcion = int(input("Seleccione una opción: "))
        except ValueError:
            print("Debe ingresar un número.")
            input("Presione Enter para continuar...")
            continue
        if opcion == 1:
            limpiar_pantalla()
            try:
                cantidad = float(input("¿Cuánto tiempo avanzar? "))
                avanzar_tiempo(cantidad)
            except ValueError as e:
                print(f"❌ Error: {e}")
            input("Presione enter para continuar....")
        elif opcion == 2:
            limpiar_pantalla()
            try:
                nuevo_tiempo = float(input("Nuevo tiempo: "))
                establecer_tiempo_actual(nuevo_tiempo)
            except ValueError as e:
                print(f"❌ Error: {e}")
            input("Presione enter para continuar....")
        elif opcion == 3:
            limpiar_pantalla()
            tiempo = float(input("Hora de inicio del evento (HH.MM): "))
            ID = input("ID del evento (no puede superar los 6 símbolos): ").strip()
            tipo = input("Tipo de evento (ATERRIZAJE, DESPEGUE, MANTENIMIENTO): ").strip().upper()
            if tipo == "MANTENIMIENTO":
                prioridad = 100
                view_airstrip_list()
                pista_id = str(input("ID de la pista a asignar. La pista debe existir anteriormente: ").strip())
                if pista_ocupada(pista_id) is None:
                    print("La pista no existe")
                    input("Presione Enter para continuar...")
                    continue
                # podrías marcarla como mantenimiento si quieres:
                if not marcar_pista_mantenimiento(pista_id):
                    print("No se pudo marcar la pista")
                avion_id = None
                piloto_id = None
                descripcion = f"Mantenimiento de la pista {pista_id}"
                duracion = float(input("Duración del evento (HH.MM): "))
            else:
                view_airstrip_list()
                pista_id = input("ID de la pista a asignar. La pista debe existir anteriormente: ").strip()
                estado_pista = pista_ocupada(pista_id)
                if estado_pista is None:
                    print("La pista no existe")
                    input("Presione Enter para continuar...")
                    continue
                if estado_pista:
                    print("Esta pista ya está ocupada")
                    input("Presione Enter para continuar...")
                    continue

                view_airplanes_list()
                avion_id = input("ID del avión a asignar. El avión debe existir anteriormente: ").strip()
                estado_avion = avion_ocupado(avion_id)
                if estado_avion is None:
                    print("Ese avion no existe")
                    input("Presione enter para continuar....")
                    continue
                if estado_avion:
                    print("Este avion ya esta ocupado")
                    input("Presione Enter para continuar...")
                    continue
                
                # prioridad según tipo de avión
                avion_tipo = (tipo_avion(avion_id) or "").strip().lower()
                if avion_tipo == "militar":
                    prioridad = 500
                elif avion_tipo == "privado":
                    prioridad = 300
                elif avion_tipo == "comercial":
                    prioridad = 250
                else:
                    prioridad = 100
                # prioridad especial
                if avion_id in ("AL2_01", "AL2_02"):
                    prioridad = 1000
                view_pilot_list()
                piloto_id = input("ID del piloto a asignar. El piloto debe existir anteriormente: ").strip()
                estado_piloto = piloto_ocupado(piloto_id)
                if estado_piloto is None:
                    print("El piloto no existe")
                    input("Presione Enter para continuar...")
                    continue
                if estado_piloto:
                    print("Este piloto ya está ocupado")
                    input("Presione Enter para continuar...")
                    continue
                piloto_tipo = (tipo_piloto(piloto_id) or "").strip().lower()
                if avion_tipo != piloto_tipo:
                    print("Este piloto no puede volar este tipo de avión")
                    input("Presione Enter para continuar...")
                    continue
                
                descripcion = input("Breve descripción del evento: ")
                duracion = float(input("Duración del evento (HH.MM): "))
            if not marcar_pista_ocupada(pista_id): # AQUÍ se marca bien la pista como ocupada
                    print("No se pudo marcar la pista")
            if avion_id:
                marcar_avion_ocupado(avion_id)
            if piloto_id:
                marcar_piloto_ocupado(piloto_id)
            # Crear evento y guardar
            create_event(ID, tiempo, avion_id, piloto_id, pista_id, tipo, duracion, descripcion, prioridad)
            save_events_json()
            save_airstrips_json()
            save_airplanes_json()
            save_pilots_json()
            input("Evento creado. Presione Enter para continuar...")
        elif opcion == 4:
            gestion_aviones()
        elif opcion == 5:
            gestion_pilotos()
        elif opcion == 6:
            gestion_pistas()
        elif opcion == 7:
            limpiar_pantalla()
            view_events_list()
            input("Presione Enter para continuar...")
        elif opcion ==8:
            evento = simular_siguiente_evento()
            if evento:
                # Preguntar si eliminar el evento simulado
                eliminar = input("¿Eliminar este evento del calendario? (sí/no): ")
                if eliminar.lower() in ['sí', 'si', 's', 'yes', 'y']:
                    from models.events import delete_event_by_id
                    if delete_event_by_id(evento.id):
                        print("✅ Evento eliminado.")
                        input("Presione enter para continuar....")
        elif opcion == 9:
            try:
                cantidad = int(input("¿Cuántos eventos simular? "))
                for i in range(cantidad):
                    print(f"\n--- Evento {i+1}/{cantidad} ---")
                    evento = simular_siguiente_evento()
                    if evento is None:
                        print("No hay más eventos.")
                        break
            except ValueError:
                print("❌ Ingrese un número válido.")
        elif opcion == 10:
            limpiar_pantalla()
            print("\n--- SIMULACIÓN PARCIAL ---")
            print("Ingrese el tiempo máximo para simular.")
            print("Ejemplo: 100.5 para 100.5 unidades de tiempo")
            try:
                tiempo_max = float(input("Tiempo máximo: "))
                if tiempo_max < 0:
                    print("❌ El tiempo debe ser positivo.")
                    continue
                simular_por_tiempo(tiempo_max)
                input("Presione enter para continuar...")
            except ValueError:
                print("❌ Entrada no válida. Debe ser un número.")
                input("Presione enter para continuar....")
        elif opcion == 11:
            limpiar_pantalla()
            simular_calendario()
            input("Presione Enter para continuar...")
        elif opcion == 12:
            limpiar_pantalla()
            confirmar = input("¿Reiniciar tiempo a 0? (sí/no): ")
            if confirmar.lower() in ['sí', 'si', 's', 'yes', 'y']:
                reiniciar_tiempo()
                input("Tiempo reiniciado. Presione enter para continuar")
        elif opcion == 13:
            limpiar_pantalla()
            print("Guardando y saliendo....")
            time.sleep(2)
            save_events_json()
            save_airstrips_json()
            save_airplanes_json()
            save_pilots_json()
            break
        else:
            print("Comando desconocido")
            input("Presione Enter para continuar...")
