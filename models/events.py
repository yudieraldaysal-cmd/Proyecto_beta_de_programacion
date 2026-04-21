# events.py 
from dataclasses import dataclass, asdict, field
from enum import Enum, auto
from typing import Optional, Dict
from uuid import uuid4
import os
import json
from models.airplane import airplanes_map, avion_libre
from models.airstrip import airstrip_map, pista_libre
from models.pilot import pilots_map, piloto_libre
from utils.time import _ensure_data_folder
import time

# ======= Variable global de tiempo =======
tiempo_actual_global = 0.0

DATA_FOLDER = 'data'
FILEPATH = 'events.json'
events_map: Dict[str, dict] = {}
class TipoEvento(Enum):
    ATERRIZAJE = auto()
    DESPEGUE = auto()
    EMERGENCIA = auto()
    MANTENIMIENTO = auto()
    FIN_OPERACION = auto()


@dataclass(order=True)
class Evento:
    id: str = field(compare=False, default_factory=lambda: str(uuid4()))  # id como string UUID
    tiempo: float = field(compare=False, default=0.0)
    piloto_id: Optional[str] = field(compare=False, default=None)
    prioridad: int = field(compare=False, default=0)
    tipo: TipoEvento = field(compare=False, default=TipoEvento.ATERRIZAJE)
    avion_id: Optional[str] = field(compare=False, default=None)   # ID legible p.e. "AL2-01"
    pista_id: Optional[str] = field(compare=False, default=None)
    duracion: float = field(compare=False, default=0.0)
    descripcion: str = field(compare=False, default="")
    

    def es_critico(self) -> bool:
        return self.tipo == TipoEvento.EMERGENCIA or self.prioridad >= 1000

    def to_dict(self) -> dict:
        d = asdict(self)
        d["tipo"] = self.tipo.name
        return d

    @staticmethod
    def from_dict(d: dict) -> "Evento":
        raw_tipo = d.get("tipo")
        if isinstance(raw_tipo, TipoEvento):
            tipo = raw_tipo
        elif isinstance(raw_tipo, str) and raw_tipo in TipoEvento.__members__:
            tipo = TipoEvento[raw_tipo]
        else:
            tipo = TipoEvento.ATERRIZAJE
        return Evento(
            tiempo=d["tiempo"],
            prioridad=d.get("prioridad", 0),
            tipo=tipo,
            pista_id=d.get("pista_id"),
            piloto_id=d.get("piloto_id"),
            avion_id=d.get("avion_id"),
            duracion=d.get("duracion", 0.0),
            descripcion=d.get("descripcion", ""),
            id=d.get("id")
        )

    def __repr__(self):
        av = self.avion_id if self.avion_id else "None"
        return (f"<Evento {self.tipo.name} t={self.tiempo:.2f} prio={self.prioridad} "
                f"av={av} dur={self.duracion}>")


def create_event(
    ID: str,
    tiempo: float,
    avion_id: Optional[str],
    piloto_id: Optional[str],
    pista_id: str,
    tipo: str,
    duracion: float,
    descripcion: str,
    prioridad: int,
):
    ID = ID.strip()
    tipo_str = tipo.strip().upper()
    if ID == "":
        return ("el campo no puede estar vacio")
    try:
        tipo_enum = TipoEvento[tipo_str]
    except KeyError:
        tipo_enum = TipoEvento.ATERRIZAJE
    event = Evento(
        id=ID,
        tiempo=tiempo,
        avion_id=avion_id,
        pista_id=pista_id,
        piloto_id=piloto_id,
        tipo=tipo_enum,
        duracion=duracion,
        descripcion=descripcion,
        prioridad=prioridad,
    )
    events_map[ID] = event.to_dict()
    return f"Event: ID: {ID}, type: {tipo_enum.name} has been added"


def get_event(ID: str):
    k = events_map.get(ID)
    return Evento.from_dict(k) if k else None


def view_events_list() -> Dict[str, dict]:
    if not events_map:
        print("There is not events on the list")
        return {}
    for ID, e in events_map.items():
        print(f"[{ID}] - Tipo: {e['tipo']} | Prioridad: {e['prioridad']} | Duracion: {e['duracion']} | Avion: {e['avion_id']} | Piloto: {e['piloto_id']} | Pista: {e['pista_id']} | Descripcion: {e['descripcion']}")
    return events_map.copy()


# ------------- Guardar y cargar -------------
def save_events_json(path: Optional[str] = None) -> None:
    _ensure_data_folder()
    if path == None:
        path = os.path.join(DATA_FOLDER, FILEPATH)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(events_map, f, ensure_ascii=False, indent=2)


def load_events_json(path: Optional[str] = None) -> None:
    _ensure_data_folder()
    global events_map
    if path == None:
        path = os.path.join(DATA_FOLDER, FILEPATH)
    
    events_map.clear()  # Limpiar diccionario existente
    
    if not os.path.exists(path):
        # No hacer nada, events_map ya está vacío
        return
    
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    
    events_map.update(raw)  # Actualizar diccionario in-place en lugar de reasignar


def simular_calendario():
    global tiempo_actual_global
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
    tiempo_actual = tiempo_actual_global

    for evento in lista_eventos:
        time.sleep(3)
        # Si el tiempo del evento es mayor al actual, "hacemos que pase el tiempo"
        if evento.tiempo > tiempo_actual:
            print(f" >>> [Tiempo: {tiempo_actual:.2f} a {evento.tiempo:.2f}] El aeropuerto está a la espera...")
            time.sleep(3)
            tiempo_actual = evento.tiempo

        # Calcular fin basándose en tu atributo duracion
        tiempo_fin = tiempo_actual + evento.duracion
        
        # Mostrar el evento
        critico_str = " [CRÍTICO]" if evento.es_critico() else ""
        print(f"[{tiempo_actual:.2f} - {tiempo_fin:.2f}] EVENTO: {evento.tipo.name}{critico_str}")
        print(f"    Avión: {evento.avion_id} | Piloto: {evento.piloto_id}| Pista: {evento.pista_id} | Desc: {evento.descripcion}")
        if evento.pista_id:
            pista_libre(evento.pista_id)
        if evento.avion_id:
            avion_libre(evento.avion_id)
        if evento.piloto_id:
            piloto_libre(evento.piloto_id)
        # Avanzar el reloj al final del evento
        tiempo_actual = tiempo_fin
        delete_event_by_id(evento.id)

    tiempo_actual_global = tiempo_actual
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

def simular_por_tiempo(
    tiempo_maximo: float,
    eliminar_simulados: bool = True,
    pedir_confirmacion_eliminar: bool = True,
) -> None:
    """Simula eventos hasta un tiempo máximo, partiendo del tiempo actual global."""
    global tiempo_actual_global
    
    if not events_map:
        print("No hay eventos programados en el mapa.")
        return

    # Usar tiempo global como punto de partida
    tiempo_inicial = tiempo_actual_global
    print(f"🚀 Iniciando simulación desde tiempo {tiempo_inicial:.2f} hasta {tiempo_maximo:.2f}")

    # Convertir el diccionario a lista de eventos
    lista_eventos = []
    for datos in events_map.values():
        try:
            lista_eventos.append(Evento.from_dict(datos))
        except Exception as e:
            print(f"Error al cargar evento: {e}")
            continue

    # Filtrar eventos que ocurren en el rango
    eventos_en_rango = [e for e in lista_eventos 
                       if tiempo_inicial <= e.tiempo <= tiempo_maximo]
    
    if not eventos_en_rango:
        print(f"No hay eventos entre {tiempo_inicial:.2f} y {tiempo_maximo:.2f}.")
        return
    
    # Ordenar eventos
    eventos_en_rango.sort(key=lambda e: (e.tiempo, -e.prioridad))
    
    print(f"\n--- SIMULACIÓN: {tiempo_inicial:.2f} → {tiempo_maximo:.2f} ---")
    
    tiempo_simulacion = tiempo_inicial
    eventos_procesados = []
    
    for evento in eventos_en_rango:
        # Avanzar al tiempo del evento si hay hueco
        if evento.tiempo > tiempo_simulacion:
            tiempo_simulacion = evento.tiempo
        
        # Calcular fin del evento
        tiempo_fin = tiempo_simulacion + evento.duracion
        
        # Verificar si el evento cabe en el tiempo restante
        if tiempo_fin > tiempo_maximo:
            print(f"⚠️  Evento incompleto: {evento.descripcion}")
            print(f"   Se necesitaría hasta {tiempo_fin:.2f} (límite: {tiempo_maximo:.2f})")
            break
        
        # Ejecutar evento
        critico_str = " [CRÍTICO]" if evento.es_critico() else ""
        print(f"[{tiempo_simulacion:.2f} → {tiempo_fin:.2f}] {evento.tipo.name}{critico_str}: {evento.descripcion}")
        
        tiempo_simulacion = tiempo_fin
        eventos_procesados.append(evento)
    
    # Actualizar tiempo global con el tiempo final de simulación
    tiempo_anterior = tiempo_actual_global
    tiempo_actual_global = tiempo_simulacion
    print(f"\n✅ Simulación completada: {len(eventos_procesados)} eventos procesados")
    print(f"📊 Tiempo avanzó de {tiempo_anterior:.2f} a {tiempo_actual_global:.2f}")
    
    # Opcional: eliminar eventos procesados
    if eliminar_simulados and eventos_procesados:
        hacer_borrado = False
        if pedir_confirmacion_eliminar:
            confirmar = input(f"\n¿Eliminar {len(eventos_procesados)} eventos ya simulados? (sí/no): ")
            hacer_borrado = confirmar.lower() in ['sí', 'si', 's', 'yes', 'y']
        else:
            hacer_borrado = True
        if hacer_borrado:
            eliminados = 0
            for evento in eventos_procesados:
                if evento.id in events_map:
                    del events_map[evento.id]
                    eliminados += 1
            if eliminados > 0:
                save_events_json()
                print(f"🗑️  Se eliminaron {eliminados} eventos del archivo JSON.")
def obtener_tiempo_actual() -> float:
    """Obtiene el tiempo actual global."""
    global tiempo_actual_global
    return tiempo_actual_global

def establecer_tiempo_actual(nuevo_tiempo: float) -> None:
    """Establece un nuevo valor para el tiempo actual global."""
    global tiempo_actual_global
    if nuevo_tiempo < 0:
        raise ValueError("El tiempo no puede ser negativo")
    tiempo_actual_global = nuevo_tiempo
    print(f"⏰ Tiempo actual establecido a: {tiempo_actual_global:.2f}")

def avanzar_tiempo(cantidad: float) -> float:
    """Avanza el tiempo global en la cantidad especificada."""
    global tiempo_actual_global
    if cantidad < 0:
        raise ValueError("No se puede retroceder el tiempo")
    
    tiempo_anterior = tiempo_actual_global
    tiempo_actual_global += cantidad
    
    # Verificar si hay eventos que ocurren durante este avance
    eventos_durante_avance = []
    for datos in events_map.values():
        evento = Evento.from_dict(datos)
        # Evento que comienza durante el avance
        if tiempo_anterior <= evento.tiempo <= tiempo_actual_global:
            eventos_durante_avance.append(evento)
    
    if eventos_durante_avance:
        eventos_durante_avance.sort(key=lambda e: e.tiempo)
        print(f"\n📅 Eventos durante el avance de tiempo ({tiempo_anterior:.2f} → {tiempo_actual_global:.2f}):")
        for evento in eventos_durante_avance:
            print(f"   • T={evento.tiempo:.2f}: {evento.tipo.name} - {evento.descripcion}")
    
    print(f"⏰ Tiempo avanzó de {tiempo_anterior:.2f} a {tiempo_actual_global:.2f} (+{cantidad:.2f})")
    return tiempo_actual_global

def reiniciar_tiempo() -> None:
    """Reinicia el tiempo global a cero."""
    global tiempo_actual_global
    tiempo_anterior = tiempo_actual_global
    tiempo_actual_global = 0.0
    print(f"🔄 Tiempo reiniciado de {tiempo_anterior:.2f} a {tiempo_actual_global:.2f}")

def mostrar_tiempo_actual() -> str:
    """Muestra el tiempo actual de forma formateada."""
    global tiempo_actual_global
    horas = int(tiempo_actual_global // 60)
    minutos = int(tiempo_actual_global % 60)
    segundos = int((tiempo_actual_global * 60) % 60)
    return f"⏰ Tiempo actual: {tiempo_actual_global:.2f} unidades ({horas:02d}:{minutos:02d}:{segundos:02d})"
def delete_event_by_id(event_id: str) -> bool:
    """
    Elimina un evento específico por su ID.
    Retorna True si se eliminó, False si no existe.
    """
    if event_id in events_map:
        del events_map[event_id]
        save_events_json()  # Guardar cambios inmediatamente
        return True
    return False

def simular_siguiente_evento() -> Optional[Evento]:
    """Simula solo el siguiente evento en el tiempo (a partir del tiempo actual global)."""
    global tiempo_actual_global
    
    if not events_map:
        print("No hay eventos programados.")
        return None
    
    # Buscar el próximo evento después del tiempo actual
    siguiente_evento = None
    tiempo_siguiente = float('inf')
    
    for datos in events_map.values():
        evento = Evento.from_dict(datos)
        if evento.tiempo >= tiempo_actual_global and evento.tiempo < tiempo_siguiente:
            siguiente_evento = evento
            tiempo_siguiente = evento.tiempo
    
    if siguiente_evento is None:
        print(f"No hay más eventos después del tiempo {tiempo_actual_global:.2f}")
        return None
    
    # Avanzar tiempo hasta el evento
    if siguiente_evento.tiempo > tiempo_actual_global:
        print(f"⏳ Esperando de {tiempo_actual_global:.2f} a {siguiente_evento.tiempo:.2f}...")
        tiempo_actual_global = siguiente_evento.tiempo
    
    # Ejecutar evento
    tiempo_fin = tiempo_actual_global + siguiente_evento.duracion
    print(f"\n🎯 EJECUTANDO EVENTO:")
    print(f"   Tipo: {siguiente_evento.tipo.name}")
    print(f"   Descripción: {siguiente_evento.descripcion}")
    print(f"   Tiempo: {tiempo_actual_global:.2f} → {tiempo_fin:.2f}")
    print(f"   Avión: {siguiente_evento.avion_id}")
    
    # Avanzar tiempo al final del evento
    tiempo_actual_global = tiempo_fin
    
    return siguiente_evento
