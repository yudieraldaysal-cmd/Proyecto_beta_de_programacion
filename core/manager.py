from models.events import Evento, events_map, save_events_json
from models.airplane import Airplane
from models.airstrip import Airstrip
from models.pilot import Pilot


    
	
def simular_calendario():
    """
    Convierte el diccionario de eventos en una línea de tiempo ordenada
    y simula el paso del tiempo procesando cada evento.
    """
    if not events_map:
        print("No hay eventos programados en el mapa.")
        return

    # 1. Convertir el diccionario a una lista de objetos Evento
    lista_eventos = []
    for datos in events_map.values():
        # Usamos tu método from_dict 
        lista_eventos.append(Evento.from_dict(datos))

    # 2. Ordenar por tiempo (y por prioridad si el tiempo es igual)
    # En Python, si ordenas por una tupla (tiempo, prioridad), resuelve empates automáticamente
    lista_eventos.sort(key=lambda e: (e.tiempo, -e.prioridad))

    print("\n--- INICIO DE LA SIMULACIÓN DEL CALENDARIO ---")
    tiempo_actual = 0.0

    for evento in lista_eventos:
        # Si el tiempo del evento es mayor al actual, "hacemos que pase el tiempo"
        if evento.tiempo > tiempo_actual:
            print(f" >>> [Tiempo: {tiempo_actual:.2f} a {evento.tiempo:.2f}] El aeropuerto está a la espera...")
            tiempo_actual = evento.tiempo

        # Calcular fin basándose en tu atributo duracion
        tiempo_fin = tiempo_actual + evento.duracion
        
        # Mostrar el evento
        critico_str = " [CRÍTICO]" if evento.es_critico() else ""
        print(f"[{tiempo_actual:.2f} - {tiempo_fin:.2f}] EVENTO: {evento.tipo.name}{critico_str}")
        print(f"    Avión: {evento.avion_id} | Pista: {evento.pista_id} | Desc: {evento.descripcion}")
        Airstrip.liberar(evento.pista_id)
        Airplane.liberar_pista(evento.avion_id)
        Pilot.deactivate(evento.pilot_id)
        # Avanzar el reloj al final del evento
        tiempo_actual = tiempo_fin
        delete_events_by_time(tiempo_actual)

    print("--- FIN DE LA PROGRAMACIÓN ---\n")
        
def delete_events_by_time(max_tiempo: float) -> int:
    """
    Elimina eventos que ya han pasado (tiempo <= max_tiempo).
    Retorna el número de eventos eliminados.
    """
    eventos_a_eliminar = []
    
    for event_id, datos in events_map.items():
        if datos.get("tiempo", float('inf')) <= max_tiempo:
            eventos_a_eliminar.append(event_id)
    
    for event_id in eventos_a_eliminar:
        del events_map[event_id]
    
    if eventos_a_eliminar:
        save_events_json()
    
    return len(eventos_a_eliminar)
