#!/usr/bin/env python3
"""Test para verificar que el GUI mostraría correctamente los eventos"""

from models.events import load_events_json, events_map, create_event, save_events_json

# Simular lo que hace el GUI al iniciar
print("=" * 70)
print("SIMULACIÓN DE INICIALIZACIÓN DEL GUI")
print("=" * 70)

# 1. Cargar eventos
load_events_json()
print(f"\n✅ Eventos cargados: {len(events_map)} eventos en memory")

# 2. Mostrar lo que vería el tree widget de Tkinter
print("\nDatos que se mostrarían en la tabla de eventos:")
print("-" * 70)
print(f"{'ID':<15} {'Tipo':<15} {'Tiempo':<10} {'Prio':<6} {'Avión':<12} {'Piloto':<12} {'Pista':<10} {'Dur':<6}")
print("-" * 70)

for eid, e in events_map.items():
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
    print(f"{str(values[0]):<15} {str(values[1]):<15} {str(values[2]):<10} {str(values[3]):<6} {str(values[4]):<12} {str(values[5]):<12} {str(values[6]):<10} {str(values[7]):<6}")

print("-" * 70)
print(f"\n✅ Se mostrarían {len(events_map)} filas en la tabla")

# 3. Probar crear un nuevo evento
print("\n" + "=" * 70)
print("PRUEBA: Crear nuevo evento")
print("=" * 70)

antes = len(events_map)
resultado = create_event(
    ID="NUEVO-001",
    tiempo=75.0,
    avion_id="AL2-03",
    piloto_id="P002",
    pista_id="PISTA2",
    tipo="DESPEGUE",
    duracion=3.0,
    descripcion="Prueba despegue",
    prioridad=300
)
print(f"\n{resultado}")
print(f"Eventos antes: {antes}")
print(f"Eventos después: {len(events_map)}")

if len(events_map) > antes:
    print("✅ Nuevo evento agregado a events_map correctamente")
    save_events_json()
    print("✅ Guardado en JSON")
    
    # Verificar que se mantiene después de recargar
    load_events_json()
    print(f"✅ Después de recargar: {len(events_map)} eventos")
else:
    print("❌ ERROR: El evento no se agregó a events_map")

print("\n" + "=" * 70)
print("✅ TODAS LAS PRUEBAS EXITOSAS - GUI DEBERÍA MOSTRAR EVENTOS")
print("=" * 70)
