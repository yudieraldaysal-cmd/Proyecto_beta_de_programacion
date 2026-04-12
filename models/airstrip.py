# airstrips.py
from dataclasses import dataclass, asdict
from typing import Optional
import json
from utils.time import airstrip_vstatus, error1, error2, error3
from utils.time import _ensure_data_folder
import os

DATA_FOLDER = "data"
FILEPATH = "pista.json"


@dataclass
class Airstrip:
    id: str
    status: str
    callsign: str
    busy_until: Optional[float] = None
    actual_plane: Optional[str] = None

    def sign_plane(self, airplane_id: str, initial_time: float, duration: float):
        self.actual_plane = airplane_id
        self.status = "ocupada"
        self.busy_until = initial_time + duration

    def liberar(self):
        self.status = "disponible"

    def is_available(self, actual_time: float) -> bool:
        if self.status == "mantenimiento":
            return False
        if self.status == "disponible":
            return True
        if self.busy_until is None or actual_time >= self.busy_until:
            self.liberar()
            return True
        return False

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Airstrip":
        return Airstrip(**d)

    def __repr__(self):
        occ = f"ocupada_hasta={self.busy_until:.2f}" if self.busy_until is not None else "libre"
        return f"<Pista {self.callsign} (ID={self.id}) estado={self.status} {occ}>"


# Repositorio en memoria: clave = ID (string), valor = dict
airstrip_map: dict[str, dict] = {}


def add_airstrip(ID: str, callsign: Optional[str] = None, status: str = "disponible") -> str:
    ID = ID.strip()
    if ID in airstrip_map:
        return error1()  # ya existe

    if callsign is None:
        callsign = ID
    callsign = callsign.strip()

    airstrip_map[ID] = {
        "ID": ID,
        "status": status,
        "callsign": callsign,
        "busy_until": None,
        "actual_plane": None,
    }
    return f"Airstrip with ID {ID} has been added."


def view_airstrip_list() -> dict:
    if not airstrip_map:
        print("There are no pistas on list")
        return {}
    for ID, pista in airstrip_map.items():
        print(
            f"[{ID}] - ID:{pista['ID']} | Status: {pista['status']} | "
            f"Callsign: {pista.get('callsign')}"
        )
    return airstrip_map.copy()


def save_airstrips_json(path: Optional[str] = None) -> None:
    _ensure_data_folder()
    if path is None:
        path = os.path.join(DATA_FOLDER, FILEPATH)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(airstrip_map, f, ensure_ascii=False, indent=2)


def load_airstrips_json(path: Optional[str] = None) -> None:
    _ensure_data_folder()
    global airstrip_map
    if path is None:
        path = os.path.join(DATA_FOLDER, FILEPATH)
    if not os.path.exists(path):
        airstrip_map = {}
        return
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    airstrip_map = raw


def pista_existe(ID: str) -> bool:
    return ID in airstrip_map


def marcar_pista_ocupada(ID: str) -> bool:
    if ID not in airstrip_map:
        return False
    airstrip_map[ID]["status"] = "ocupada"
    save_airstrips_json()
    return True


def marcar_pista_mantenimiento(ID: str) -> bool:
    if ID not in airstrip_map:
        return False
    airstrip_map[ID]["status"] = "mantenimiento"
    save_airstrips_json()
    return True


def pista_ocupada(ID: str) -> Optional[bool]:
    """None = ID inexistente; True = no disponible; False = libre."""
    if ID not in airstrip_map:
        return None
    return airstrip_map[ID]["status"] in ("ocupada", "mantenimiento")


def pista_libre(ID: str) -> bool:
    if ID not in airstrip_map:
        return False
    airstrip_map[ID]["status"] = "disponible"
    save_airstrips_json()
    return True
