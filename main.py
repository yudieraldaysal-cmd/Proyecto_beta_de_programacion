# main.py
import sys

from models.airplane import load_airplanes_json
from models.airstrip import load_airstrips_json
from models.events import load_events_json
from models.pilot import load_pilots_json

load_airplanes_json()
load_pilots_json()
load_events_json()
load_airstrips_json()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--gui", "-g"):
        from ui.gui import run_app

        run_app()
    else:
        from ui.menu import main

        main()
