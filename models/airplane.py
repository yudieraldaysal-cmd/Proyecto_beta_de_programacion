# airplanes.py
from dataclasses import dataclass, asdict
from typing import Optional, Dict
import json
import os

from utils.time import _ensure_data_folder
from utils.time import error1, error2, error3, validate_types
from models.pilot import pilots_map

DATA_FOLDER = "data"
FILEPATH = "avion.json"

# Repositorio en memoria: clave = ID (string) -> valor = dict (serializable) o Airplane.to_dict()
airplanes_map: Dict[str, dict] = {}


@dataclass(order=True)
class Airplane:
    id: str
    airplane_type: str
    status: str = "disponible"
    assigned_airstrip: Optional[str] = None
    priority: int = 0
    pilot_id: Optional[str] = None

    def emergency(self):
        self.priority = max(self.priority, 1000)
        self.status = "emergency"

    def asignar_pista(self, pista: str):
        self.assigned_airstrip = pista
        self.status = "ocupado"

    def liberar_pista(self):
        self.assigned_airstrip = None
        self.status = "libre"

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Airplane":
        return Airplane(**d)

    def __repr__(self):
        cid = self.id[:6] if self.id else self.id
        # self.callsign no existe en la clase; lo quito o lo sustituyo por id  # <--
        return (f"<Avion {cid} tipo={self.airplane_type} "
                f"prio={self.priority} estado={self.status}>")


# ---------- Operaciones sobre el mapa ----------

def add_airplane(ID: str, airplane_type: str, pilot_id: Optional[str] = None) -> str:
    ID = ID.strip()
    airplane_type = airplane_type.strip().lower() if airplane_type else ""

    # Validaciones básicas
    if not ID:
        return error3()
    if len(ID) > 12:  # ajustable
        return error2()
    if airplane_type not in validate_types:
        return error2()

    # Validar piloto (si se pasa)
    if pilot_id:
        if pilot_id not in pilots_map:
            return error2()

    # Evitar duplicados por ID (clave del mapa)
    if ID in airplanes_map:
        return error1()

    status = "disponible"
    plane = Airplane(id=ID, airplane_type=airplane_type, pilot_id=None, status=status)
    airplanes_map[ID] = plane.to_dict()
    return f"Airplane {ID} has been added."


def get_airplane(ID: str) -> Optional[Airplane]:
    d = airplanes_map.get(ID)
    return Airplane.from_dict(d) if d else None


def view_airplanes_list() -> Dict[str, dict]:
    if not airplanes_map:
        print("There are no airplanes on list")
        return {}
    for ID, plane in airplanes_map.items():
        print(f"[{ID}] - Type: {plane['airplane_type']} | "
              f"Pilot: {plane.get('pilot_id')} | Status: {plane['status']}")
    return airplanes_map.copy()


# ---------- Persistencia JSON ----------

def save_airplanes_json(path: Optional[str] = None) -> None:
    _ensure_data_folder()
    if path is None:
        path = os.path.join(DATA_FOLDER, FILEPATH)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(airplanes_map, f, ensure_ascii=False, indent=2)


def load_airplanes_json(path: Optional[str] = None) -> None:
    _ensure_data_folder()
    global airplanes_map
    if path is None:
        path = os.path.join(DATA_FOLDER, FILEPATH)
    
    airplanes_map.clear()  # Limpiar diccionario existente
    
    if not os.path.exists(path):
        # No hacer nada, airplanes_map ya está vacío
        return
    
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    
    airplanes_map.update(raw)  # Actualizar diccionario in-place


# ---------- Utilidades ----------

def assign_pilot_to_airplane(airplane_id: str, pilot_id: str) -> str:
    if not airplanes_map:
        print("There are not airplanes")
        return
    if pilot_id not in pilots_map:
        return "El piloto no existe"
    if airplanes_map[airplane_id]["pilot_id"] is not None:
        return "El avion ya tiene asigando un piloto"
    if pilots_map[pilot_id]["status"] == "ocupado":
        return "El piloto ya tiene vuelo asignado"

    airplanes_map[airplane_id]["pilot_id"] = pilot_id
    pilots_map[pilot_id]["status"] = "ocupado"
    return f"Pilot {pilot_id} assigned to airplane {airplane_id}."


def avion_existe(ID: str) -> bool:
    return ID in airplanes_map


def marcar_avion_ocupado(ID: str) -> bool:
    if ID not in airplanes_map:
        return False
    airplanes_map[ID]["status"] = "ocupado"
    save_airplanes_json()
    return True


def marcar_avion_mantenimiento(ID: str) -> bool:
    if ID not in airplanes_map:
        return False
    airplanes_map[ID]["status"] = "mantenimiento"
    save_airplanes_json()
    return True


def avion_ocupado(ID: str) -> Optional[bool]:
    """None = ID inexistente; True = ocupado o en mantenimiento; False = disponible."""
    if ID not in airplanes_map:
        return None
    return airplanes_map[ID]["status"] in ("ocupado", "mantenimiento")


def tipo_avion(ID: str) -> str:
    if ID not in airplanes_map:
        return "El avion no existe"
    return airplanes_map[ID].get("airplane_type")  # <--
    

def avion_libre(ID: str) -> bool:
    if ID not in airplanes_map:
        return False
    airplanes_map[ID]["status"] = "disponible"
    save_airplanes_json()
    return True
