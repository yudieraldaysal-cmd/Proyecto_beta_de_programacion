# INICIO
Buenas tardes, es Yudier Alday, alumno de CC, del C111. El proyecto a continuacion es algo simple, es un gestor de eventos basado en la simulacion basica de una torre de control, con diferentes eventos tipo despegue, aterrizaje, mantenimiento. Al entrar podemos ver, en la parte superior el nombre del programa y su menu principal, justo abajo el tiempo actual del programa (que comienza en el 00:00 o 0.00 unidades). Que hice para obtener el tiempo? facil (y nos estamos adelantando un poco) creamos una funcion que nos diera el tiempo actual del proyecto, el cual comienza en 00:00, bueno, ya que estamos en como funciona el tiempo, vamos a explicarlo

## Avanzando el tiempo
Comentamos antes que creamos una funcion para establecer y obtener el tiempo actual, simplemente asigamos `tiempo_actual = 0.00`, nada dificil. Pero como trabajo para que avance el tiempo? Decimos cuanto queremos avanzar en unidades positivas, eso fija el tiempo actual como:
```python
#para manejar el aumento del tiempo
tiempo_anterior = tiempo_actual
tiempo_actual = tiempo_anterior + cantidad
```
lo he puesto asi por que nuestra funcion creada maneja la variable global tiempo_actual y la modifica. Tras el avance revisamos si existen eventos los cuales se deben de procesar (y hay algo programado a las 2 y ya son las 3, el evento debio pasar ya), comenzamos con un diccionario vacio (eventos_durante_avance = []) y hacemos:
```python
eventos_durante_avance = []
    for datos in events_map.values():
        evento = Evento.from_dict(datos)
        if tiempo_anterior <= evento.tiempo <= tiempo_actual_global:
            eventos_durante_avance.append(evento)
    
    if eventos_durante_avance:
        eventos_durante_avance.sort(key=lambda e: e.tiempo)
        print(f"Eventos durante el avance de tiempo ({tiempo_anterior:.2f} -> {tiempo_actual_global:.2f}):")
        for evento in eventos_durante_avance:
            print(f"   T={evento.tiempo:.2f}: {evento.tipo.name} - {evento.descripcion}")
```
que hacemos aqui? basicamente, revisamos todos los eventos que tenemos guardados y si su tiempo de ejecucion esta entre el tiempo anterior y el nuevo tiempo al que avanzamos, lo reportamos. Esto permite que el programa "se ponga al dia" con eventos que debieron ocurrir mientras el tiempo avanzaba. El sistema de tiempo es modular y se encuentra en el archivo `models/events.py` con funciones como `avanzar_tiempo()`, `establecer_tiempo_actual()`, `reiniciar_tiempo()` y `mostrar_tiempo_actual()`.

## Arquitectura del proyecto

Vamos a comentar un poco la estructura que tiene el proyecto para que se entienda mejor como esta armado:

```
torre_control/
├── main.py              # Punto de entrada
├── models/
│   ├── airplane.py      # Aviones: CRUD + persistencia JSON
│   ├── airstrip.py      # Pistas: CRUD + persistencia JSON
│   ├── pilot.py         # Pilotos: CRUD + persistencia JSON
│   └── events.py        # Eventos + tiempo + simulacion
├── ui/
│   └── menu.py          # Interfaz de terminal
├── utils/
│   ├── utils.py         # Utilidades: menus de gestion
│   └── time.py          # Errores, validacion, carpeta data
├── data/                # Archivos JSON de persistencia
└── report.md            # Este reporte
```

Separar el proyecto en modulos me ayudo muchisimo a mantener el codigo organizado y entendible. Cada modelo tiene su propio archivo, y cada uno se encarga de su propia logica de negocio y persistencia. Como profesor me enseñaron, "divide y venceras", y la verdad es que funciona.

## Los modelos de datos

Cada entidad del mundo real la modele como una dataclass de Python. Esto me ahorro escribir decenas de lineas de codigo repetitivo (constructores, metodos `__repr__`, etc.).

### Airplane
```python
@dataclass(order=True)
class Airplane:
    id: str
    airplane_type: str       # comercial, militar, carga, privado
    status: str = "disponible"
    assigned_airstrip: Optional[str] = None
    priority: int = 0
    pilot_id: Optional[str] = None
```
Tiene metodos como `emergency()` que sube la prioridad a 1000, `asignar_pista()` que marca el avion como ocupado con una pista asignada, y `liberar_pista()` que lo devuelve a disponible.

### Pilot
```python
@dataclass(order=True)
class Pilot:
    id: str
    first_name: str
    last_name: str
    airplane_type: str
    status: str = "disponible"
    priority: int = 0
```
Los pilotos tienen una propiedad `name` que devuelve el nombre completo, y metodos `activate()`, `deactivate()`, `emergency()` para cambiar su estado.

### Airstrip
```python
@dataclass
class Airstrip:
    id: str
    status: str
    callsign: str
    busy_until: Optional[float] = None
    actual_plane: Optional[str] = None
```
Las pistas tienen un metodo interesante: `is_available()`. Este verifica si la pista esta disponible en un tiempo dado. Si la pista estaba ocupada pero ya paso el tiempo de ocupacion (`busy_until`), automaticamente la libera:
```python
def is_available(self, actual_time: float) -> bool:
    if self.status == "mantenimiento":
        return False
    if self.status == "disponible":
        return True
    if self.busy_until is None or actual_time >= self.busy_until:
        self.liberar()
        return True
    return False
```

### Evento
```python
@dataclass(order=True)
class Evento:
    id: str
    tiempo: float
    piloto_id: Optional[str] = None
    prioridad: int = 0
    tipo: TipoEvento           # ATERRIZAJE, DESPEGUE, EMERGENCIA, MANTENIMIENTO, FIN_OPERACION
    avion_id: Optional[str] = None
    pista_id: Optional[str] = None
    duracion: float = 0.0
    descripcion: str = ""
```
El evento es la pieza central del programa. Cada evento tiene un tiempo en el que debe ocurrir, una duracion, y referencias a un avion, piloto y pista. El metodo `es_critico()` devuelve True si es una emergencia o si la prioridad es >= 1000.

## Los mapas en memoria

Algo curioso de mi implementacion es que uso diccionarios globales como repositorios en memoria. Por ejemplo:
```python
airplanes_map: Dict[str, dict] = {}
pilots_map: Dict[str, dict] = {}
airstrip_map: dict[str, dict] = {}
events_map: Dict[str, dict] = {}
```
Todos almacenan sus datos como diccionarios planos (no objetos). Cuando necesito trabajar con un objeto, uso `from_dict()` para convertir el dict a una dataclass, y cuando lo guardo uso `to_dict()`. Esto me facilito mucho la serializacion a JSON, que es basicamente un diccionario, no tuve que hacer ninguna conversion rara.

## Persistencia con JSON

Cada modelo tiene sus funciones `save_*_json()` y `load_*_json()` que guardan y cargan los datos desde archivos JSON en la carpeta `data/`. El proceso es sencillo:
1. `load_*_json()`: limpia el mapa, verifica que el archivo exista, carga el JSON y actualiza el mapa.
2. `save_*_json()`: escribe el mapa completo como JSON formateado.

Esto permite que los datos persistan entre ejecuciones del programa. Los archivos JSON son legibles y editables manualmente si se necesita.

## Validaciones y errores

En `utils/time.py` defini funciones de error simples:
```python
def error1():
    print("Elemento duplicado")
def error2():
    print("Elemento invalido")
def error3():
    print("El campo no puede estar vacio")
```
Y tambien una lista de tipos de avion validos: `["comercial", "militar", "carga", "privado"]`. Cada funcion `add_*()` en los modelos valida que los campos sean correctos, que no haya duplicados, y que los tipos sean validos. Por ejemplo, en `airplane.py` la funcion `add_airplane()` verifica que el ID no este vacio, que no supere los 12 caracteres, que el tipo este dentro de los validos, y que el ID no este duplicado.

Tambien hay validaciones entre modelos. Por ejemplo, al crear un evento de despegue o aterrizaje, se verifica que el piloto pueda volar ese tipo de avion, que la pista no este ocupada, que el avion este disponible, etc.

## Interfaz CLI

El menu principal se encuentra en `ui/menu.py`. Las opciones son:
1. **Avanzar el tiempo** - Adelanta el reloj y muestra eventos que ocurren durante el avance
2. **Establecer tiempo especifico** - Salta directamente a un tiempo dado
3. **Agregar evento** - Crea un nuevo evento con todas sus validaciones
4. **Gestionar aviones** - Submenu para agregar/ver/guardar aviones
5. **Gestionar pilotos** - Submenu para agregar/ver/guardar pilotos
6. **Gestionar pistas** - Submenu para agregar/ver/guardar pistas
7. **Ver eventos** - Lista todos los eventos programados
8. **Simular siguiente evento** - Ejecuta el proximo evento en la linea de tiempo
9. **Simular varios eventos** - Ejecuta N eventos siguientes
10. **Simular calendario por tiempo** - Simula hasta un tiempo maximo
11. **Simular calendario completo** - Simula todos los eventos del tirón
12. **Reiniciar el tiempo a 0** - Vuelve el reloj a cero
13. **Salir** - Guarda todo y cierra

Cada submenu sigue el mismo patron: un bucle `while True` que muestra las opciones, pide una entrada numerica, y ejecuta la accion correspondiente con validacion de errores. La funcion `limpiar_pantalla()` de `utils/utils.py` mantiene la terminal ordenada.

## Simulacion de eventos

El corazon del programa son las funciones de simulacion en `models/events.py`:

### `simular_calendario()`
Convierte todos los eventos del mapa a objetos `Evento`, los ordena por tiempo (y prioridad descendente para desempates), y los ejecuta uno por uno con pausas de 3 segundos (`time.sleep(3)`) para simular el paso del tiempo. Al finalizar cada evento, libera los recursos (pista, avion, piloto) y elimina el evento del mapa.

### `simular_por_tiempo()`
Similar a la anterior pero limitada a un rango de tiempo. Muestra eventos que ocurren desde el tiempo actual hasta un tiempo maximo especificado por el usuario. Si un evento no cabe en el tiempo restante, muestra una advertencia y detiene la simulacion. Tiene opcion de eliminar los eventos simulados con confirmacion del usuario.

### `simular_siguiente_evento()`
Busca el evento mas cercano en el tiempo (a partir del tiempo actual global), avanza el reloj hasta ese momento, y ejecuta el evento. Muestra los detalles del evento y avanza el tiempo al final del mismo. Retorna el evento ejecutado (o None si no hay mas eventos).

### `avanzar_tiempo()`
Adelanta el tiempo global en una cantidad especifica y verifica si hay eventos en ese intervalo, reportandolos. Es la funcion que se usa desde el menu principal opcion 1.

## Archivos de prueba

Inclui un script de prueba:
- `test_eventos_debug.py`: Diagnostica que los datos se carguen correctamente desde el JSON de eventos, verificando su estructura.

Este script me ayudo a depurar problemas de visualizacion de eventos.

## Datos de ejemplo

El proyecto viene con datos precargados en la carpeta `data/` para hacer pruebas:
- **Aviones**: AL2-01 (privado, ocupado), NOEL06 (militar, disponible), AL2-02 y AL2-03 (privados)
- **Pilotos**: PIL-01 Alberto Rodriguez (privado, ocupado), PIL-02 Brayhant Chavez (militar, disponible), PIL-12 Juan Pedro Azula (privado, ocupado)
- **Pistas**: P-01 (ocupada), A-01 (ocupada), P-19 (disponible)
- **Eventos**: Dos eventos de despegue programados para tiempo 56.0 con duracion 10.0

Los aviones AL2-01 y AL2-02 tienen prioridad especial 1000 en el codigo (esto esta hardcodeado como una caracteristica especial).

## Modo de uso

Para ejecutar el programa:
```bash
python main.py
```

Al iniciar, el programa carga automaticamente todos los datos desde los archivos JSON y se muestra el menu principal con las 13 opciones. Al cerrar el programa (opcion 13), se guardan todos los datos automaticamente.

## Posibles mejoras futuras

El proyecto es funcional pero hay varias cosas que se podrian mejorar:
1. Agregar una base de datos real (SQLite por ejemplo) en lugar de JSON para manejar datos mas grandes.
2. Anadir sonidos o notificaciones cuando ocurren eventos criticos.
3. Implementar una simulacion mas realista con tiempos aleatorios y generacion automatica de eventos.
4. Agregar reportes y estadisticas (cantidad de vuelos por dia, horas de operacion, etc.).
5. Separar el archivo `events.py` que se ha vuelto bastante grande (408 lineas) en modulos mas pequenos.
6. Mejorar el sistema de prioridades para que sea configurable por el usuario.
7. Anadir un modo multijugador o multiplayer donde varios usuarios puedan gestionar el aeropuerto simultaneamente (esto seria un proyecto aparte ya con redes de por medio).

## Conclusion

En resumen, este proyecto de Torre de Control fue una experiencia de aprendizaje enorme. Aplique conceptos de programacion orientada a objetos (dataclasses, herencia de Enum), manejo de archivos JSON, diseno de interfaces de usuario en terminal, y diseno modular. Aunque es un proyecto sencillo, me permitio consolidar muchos conocimientos de Programacion I.

El codigo fuente completo esta disponible en el repositorio y cualquier persona con Python 3.12+ puede ejecutarlo sin instalar dependencias adicionales. Eso fue algo que me propuse desde el principio: que el proyecto fuera 100% autocontenido con la biblioteca estandar.

Personalmente, lo que mas disfrute fue programar la simulacion del calendario, porque ahi se ve el programa "cobrar vida" cuando los eventos se ejecutan uno tras otro mostrando el paso del tiempo.

Y bueno, eso es basicamente todo lo que les puedo contar de mi proyecto de Torre de Control. Cualquier duda o sugerencia, estoy abierto a comentarios. Gracias por leer hasta aqui.
