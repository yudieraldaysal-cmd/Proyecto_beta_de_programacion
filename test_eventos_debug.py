#!/usr/bin/env python3
"""Script de prueba para diagnosticar el problema con la lista de eventos en GUI"""

from models.events import load_events_json, events_map

# Reproducir lo que hace el GUI
load_events_json()

print("=" * 60)
print("DIAGNÓSTICO DE EVENTOS EN GUI")
print("=" * 60)
print(f"\n1. events_map cargado: {bool(events_map)}")
print(f"2. Número de eventos: {len(events_map)}")
print(f"3. IDs: {list(events_map.keys())}")

if events_map:
    print("\n4. Estructura del primer evento:")
    first_event = list(events_map.values())[0]
    print(f"   Tipo: {type(first_event)}")
    print(f"   Keys: {first_event.keys()}")
    print(f"   Contenido:")
    for key, value in first_event.items():
        print(f"      {key}: {value} (tipo: {type(value).__name__})")
    
    print("\n5. Prueba de acceso como hace GUI:")
    e = first_event
    eid = list(events_map.keys())[0]
    values = (
        eid,
        e.get("tipo", ""),
        e.get("tiempo", ""),
        e.get("prioridad", ""),
        e.get("avion_id") or "",
        e.get("piloto_id") or "",
        e.get("pista_id") or "",
        e.get("duracion", ""),
    )
    print(f"   Valores formateados: {values}")
    print(f"   Longitud: {len(values)} (esperado: 8)")
else:
    print("\n⚠️  events_map está VACÍO")
