# pilots.py
from dataclasses import dataclass, asdict
from typing import Optional, Dict
import json
import os

from utils.time import _ensure_data_folder
from utils.time import error1, error2, error3, validate_types, pilot_vstatus

DATA_FOLDER = "data"
FILEPATH = "piloto.json"

# Repositorio en memoria: clave = ID string -> valor = dict serializable
pilots_map: Dict[str, dict] = {}


@dataclass(order=True)
class Pilot:
    id: str
    first_name: str
    last_name: str
    airplane_type: str
    status: str = "disponible"
    priority: int = 0

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def activate(self):
        self.status = "activo"

    def deactivate(self):
        self.status = "disponible"

    def emergency(self):
        self.priority = max(self.priority, 1000)
        self.status = "emergency"

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Pilot":
        return Pilot(**d)

    def __repr__(self):
        return (f"<Pilot {self.name} (ID={self.id}) "
                f"type={self.airplane_type} prio={self.priority} status={self.status}>")


# ---------- Operaciones ----------

def validate_pilot_fields(ID: str, first_name: str, last_name: str, airplane_type: str) -> Optional[str]:
    ID = (ID or "").strip()
    first_name = (first_name or "").strip()
    last_name = (last_name or "").strip()
    airplane_type = (airplane_type or "").strip().lower()

    if not ID:
        return error3()
    if len(ID) > 12:
        return error2()
    if not first_name or not last_name:
        return error3()
    if airplane_type not in validate_types:
        return error2()
    return None


def add_pilot(ID: str, first_name: str, last_name: str, airplane_type: str) -> str:
    err = validate_pilot_fields(ID, first_name, last_name, airplane_type)
    if err:
        return err

    ID = ID.strip()
    airplane_type = airplane_type.strip().lower()

    # Evitar duplicados por ID (clave del mapa)
    if ID in pilots_map:
        return error1()

    pilot = Pilot(
        id=ID,
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        airplane_type=airplane_type,
    )
    pilots_map[ID] = pilot.to_dict()
    return f"Pilot {ID} has been added."


def get_pilot(ID: str) -> Optional[Pilot]:
    d = pilots_map.get(ID)
    return Pilot.from_dict(d) if d else None


def view_pilot_list() -> Dict[str, dict]:
    if not pilots_map:
        print("There is no pilot on list")
        return {}
    for ID, p in pilots_map.items():
        print(f"[{ID}] - Name: {p['first_name']} {p['last_name']} | "
              f"Type: {p['airplane_type']} | Status: {p['status']}")
    return pilots_map.copy()


# ---------- Persistencia JSON ----------

def save_pilots_json(path: Optional[str] = None) -> None:
    _ensure_data_folder()
    if path is None:
        path = os.path.join(DATA_FOLDER, FILEPATH)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(pilots_map, f, ensure_ascii=False, indent=2)


def load_pilots_json(path: Optional[str] = None) -> None:
    _ensure_data_folder()
    global pilots_map
    if path is None:
        path = os.path.join(DATA_FOLDER, FILEPATH)
    
    pilots_map.clear()  # Limpiar diccionario existente
    
    if not os.path.exists(path):
        # No hacer nada, pilots_map ya está vacío
        return
    
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    
    pilots_map.update(raw)  # Actualizar diccionario in-place


# ---------- Utilidades ----------

def piloto_existe(ID: str) -> bool:
    return ID in pilots_map


def marcar_piloto_ocupado(ID: str) -> bool:
    if ID not in pilots_map:
        return False
    pilots_map[ID]["status"] = "ocupado"
    save_pilots_json()
    return True


def piloto_ocupado(ID: str) -> Optional[bool]:
    """None = ID inexistente; True = ocupado; False = disponible."""
    if ID not in pilots_map:
        return None
    return pilots_map[ID]["status"] == "ocupado"


def tipo_piloto(ID: str) -> str:
    if ID not in pilots_map:
        return "El piloto no existe"
    return pilots_map[ID].get("airplane_type")  # <-- ahora devuelve algo


def piloto_libre(ID: str) -> bool:
    if ID not in pilots_map:
        return False
    pilots_map[ID]["status"] = "disponible"
    save_pilots_json()
    return True
