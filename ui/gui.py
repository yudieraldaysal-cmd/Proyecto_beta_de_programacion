# gui.py — interfaz Tkinter para Torre de Control
from __future__ import annotations

import contextlib
import io
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from models.airplane import (
    add_airplane,
    airplanes_map,
    avion_ocupado,
    load_airplanes_json,
    marcar_avion_ocupado,
    save_airplanes_json,
    tipo_avion,
)
from models.airstrip import (
    add_airstrip,
    airstrip_map,
    load_airstrips_json,
    marcar_pista_mantenimiento,
    marcar_pista_ocupada,
    pista_ocupada,
    save_airstrips_json,
)
from models.events import (
    avanzar_tiempo,
    create_event,
    delete_event_by_id,
    establecer_tiempo_actual,
    events_map,
    load_events_json,
    mostrar_tiempo_actual,
    reiniciar_tiempo,
    save_events_json,
    simular_calendario,
    simular_por_tiempo,
    simular_siguiente_evento,
)
from models.pilot import (
    add_pilot,
    load_pilots_json,
    marcar_piloto_ocupado,
    piloto_ocupado,
    pilots_map,
    save_pilots_json,
    tipo_piloto,
)


def _capture_stdout(fn, *args, **kwargs) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            fn(*args, **kwargs)
        except Exception as e:
            return f"Error: {e}\n"
    return buf.getvalue()


class TorreControlGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Torre de Control")
        self.geometry("920x640")
        self.minsize(760, 520)

        load_airplanes_json()
        load_pilots_json()
        load_events_json()
        load_airstrips_json()

        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self._build_tab_inicio(nb)
        self._build_tab_eventos(nb)
        self._build_tab_flota(nb)
        self._build_tab_simulacion(nb)
        self._build_tab_log(nb)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ——— Log ———
    def log(self, text: str) -> None:
        self._log.insert(tk.END, text.rstrip() + "\n")
        self._log.see(tk.END)

    def _build_tab_log(self, nb: ttk.Notebook) -> None:
        f = ttk.Frame(nb, padding=8)
        nb.add(f, text="Consola")
        self._log = scrolledtext.ScrolledText(f, height=24, wrap=tk.WORD, font=("Consolas", 10))
        self._log.pack(fill=tk.BOTH, expand=True)

    def _build_tab_inicio(self, nb: ttk.Notebook) -> None:
        f = ttk.Frame(nb, padding=12)
        nb.add(f, text="Inicio / Reloj")

        self._lbl_tiempo = ttk.Label(f, text=mostrar_tiempo_actual(), font=("Segoe UI", 12))
        self._lbl_tiempo.pack(anchor=tk.W, pady=(0, 16))

        row = ttk.Frame(f)
        row.pack(anchor=tk.W, pady=4)
        ttk.Label(row, text="Avanzar tiempo:").pack(side=tk.LEFT)
        self._var_avance = tk.StringVar(value="10")
        ttk.Entry(row, textvariable=self._var_avance, width=10).pack(side=tk.LEFT, padx=6)
        ttk.Button(row, text="Aplicar", command=self._cmd_avanzar).pack(side=tk.LEFT)

        row2 = ttk.Frame(f)
        row2.pack(anchor=tk.W, pady=8)
        ttk.Label(row2, text="Establecer tiempo:").pack(side=tk.LEFT)
        self._var_tiempo_set = tk.StringVar(value="0")
        ttk.Entry(row2, textvariable=self._var_tiempo_set, width=10).pack(side=tk.LEFT, padx=6)
        ttk.Button(row2, text="Establecer", command=self._cmd_establecer_tiempo).pack(side=tk.LEFT)

        ttk.Button(f, text="Reiniciar tiempo a 0", command=self._cmd_reiniciar).pack(anchor=tk.W, pady=12)
        ttk.Button(f, text="Actualizar etiqueta de tiempo", command=self._refresh_tiempo_label).pack(anchor=tk.W)

    def _refresh_tiempo_label(self) -> None:
        self._lbl_tiempo.config(text=mostrar_tiempo_actual())

    def _cmd_avanzar(self) -> None:
        try:
            c = float(self._var_avance.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido.")
            return
        out = _capture_stdout(avanzar_tiempo, c)
        self.log(out)
        self._refresh_tiempo_label()

    def _cmd_establecer_tiempo(self) -> None:
        try:
            t = float(self._var_tiempo_set.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido.")
            return
        try:
            out = _capture_stdout(establecer_tiempo_actual, t)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        self.log(out)
        self._refresh_tiempo_label()

    def _cmd_reiniciar(self) -> None:
        if not messagebox.askyesno("Confirmar", "¿Reiniciar el tiempo global a 0?"):
            return
        out = _capture_stdout(reiniciar_tiempo)
        self.log(out)
        self._refresh_tiempo_label()

    # ——— Eventos ———
    def _build_tab_eventos(self, nb: ttk.Notebook) -> None:
        f = ttk.Frame(nb, padding=8)
        nb.add(f, text="Eventos")

        form = ttk.LabelFrame(f, text="Nuevo evento", padding=8)
        form.pack(fill=tk.X, pady=(0, 8))

        g = 0
        ttk.Label(form, text="ID evento:").grid(row=g, column=0, sticky=tk.W, pady=2)
        self._ev_id = tk.StringVar()
        ttk.Entry(form, textvariable=self._ev_id, width=20).grid(row=g, column=1, sticky=tk.W, padx=6)
        g += 1

        ttk.Label(form, text="Tiempo inicio:").grid(row=g, column=0, sticky=tk.W, pady=2)
        self._ev_tiempo = tk.StringVar()
        ttk.Entry(form, textvariable=self._ev_tiempo, width=12).grid(row=g, column=1, sticky=tk.W, padx=6)
        g += 1

        ttk.Label(form, text="Tipo:").grid(row=g, column=0, sticky=tk.W, pady=2)
        self._ev_tipo = tk.StringVar(value="ATERRIZAJE")
        ttk.Combobox(
            form,
            textvariable=self._ev_tipo,
            values=("ATERRIZAJE", "DESPEGUE", "MANTENIMIENTO"),
            state="readonly",
            width=18,
        ).grid(row=g, column=1, sticky=tk.W, padx=6)
        g += 1

        ttk.Label(form, text="ID pista:").grid(row=g, column=0, sticky=tk.W, pady=2)
        self._ev_pista = tk.StringVar()
        ttk.Entry(form, textvariable=self._ev_pista, width=16).grid(row=g, column=1, sticky=tk.W, padx=6)
        g += 1

        ttk.Label(form, text="ID avión (vacío si mant.):").grid(row=g, column=0, sticky=tk.W, pady=2)
        self._ev_avion = tk.StringVar()
        ttk.Entry(form, textvariable=self._ev_avion, width=16).grid(row=g, column=1, sticky=tk.W, padx=6)
        g += 1

        ttk.Label(form, text="ID piloto (vacío si mant.):").grid(row=g, column=0, sticky=tk.W, pady=2)
        self._ev_piloto = tk.StringVar()
        ttk.Entry(form, textvariable=self._ev_piloto, width=16).grid(row=g, column=1, sticky=tk.W, padx=6)
        g += 1

        ttk.Label(form, text="Duración:").grid(row=g, column=0, sticky=tk.W, pady=2)
        self._ev_dur = tk.StringVar(value="1")
        ttk.Entry(form, textvariable=self._ev_dur, width=12).grid(row=g, column=1, sticky=tk.W, padx=6)
        g += 1

        ttk.Label(form, text="Descripción:").grid(row=g, column=0, sticky=tk.W, pady=2)
        self._ev_desc = tk.StringVar()
        ttk.Entry(form, textvariable=self._ev_desc, width=40).grid(row=g, column=1, sticky=tk.W, padx=6)
        g += 1

        ttk.Button(form, text="Crear evento", command=self._cmd_crear_evento).grid(row=g, column=1, sticky=tk.W, pady=8)

        list_f = ttk.LabelFrame(f, text="Lista de eventos", padding=4)
        list_f.pack(fill=tk.BOTH, expand=True)
        cols = ("id", "tipo", "tiempo", "prio", "avion", "piloto", "pista", "dur")
        self._tree_ev = ttk.Treeview(list_f, columns=cols, show="headings", height=10)
        for c, w in zip(cols, (100, 100, 70, 50, 90, 90, 80, 50)):
            self._tree_ev.heading(c, text=c)
            self._tree_ev.column(c, width=w)
        sb = ttk.Scrollbar(list_f, orient=tk.VERTICAL, command=self._tree_ev.yview)
        self._tree_ev.configure(yscrollcommand=sb.set)
        self._tree_ev.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        bf = ttk.Frame(f)
        bf.pack(fill=tk.X, pady=4)
        ttk.Button(bf, text="Refrescar lista", command=self._refresh_eventos_tree).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="Eliminar seleccionado", command=self._cmd_borrar_evento).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="Guardar JSON", command=self._cmd_save_events).pack(side=tk.LEFT, padx=2)

        self._refresh_eventos_tree()

    def _refresh_eventos_tree(self) -> None:
        for i in self._tree_ev.get_children():
            self._tree_ev.delete(i)
        for eid, e in events_map.items():
            self._tree_ev.insert(
                "",
                tk.END,
                values=(
                    eid,
                    e.get("tipo", ""),
                    e.get("tiempo", ""),
                    e.get("prioridad", ""),
                    e.get("avion_id") or "",
                    e.get("piloto_id") or "",
                    e.get("pista_id") or "",
                    e.get("duracion", ""),
                ),
            )

    def _cmd_save_events(self) -> None:
        save_events_json()
        messagebox.showinfo("OK", "Eventos guardados.")

    def _cmd_borrar_evento(self) -> None:
        sel = self._tree_ev.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un evento en la tabla.")
            return
        vals = self._tree_ev.item(sel[0], "values")
        eid = vals[0]
        if delete_event_by_id(str(eid)):
            self.log(f"Evento eliminado: {eid}")
            self._refresh_eventos_tree()
        else:
            messagebox.showerror("Error", "No se pudo eliminar.")

    def _cmd_crear_evento(self) -> None:
        try:
            tiempo = float(self._ev_tiempo.get().replace(",", "."))
            duracion = float(self._ev_dur.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Error", "Tiempo y duración deben ser números.")
            return

        ID = self._ev_id.get().strip()
        tipo = self._ev_tipo.get().strip().upper()
        pista_id = self._ev_pista.get().strip()
        avion_id = self._ev_avion.get().strip() or None
        piloto_id = self._ev_piloto.get().strip() or None
        descripcion = self._ev_desc.get().strip()

        if not ID:
            messagebox.showerror("Error", "El ID del evento no puede estar vacío.")
            return

        if tipo == "MANTENIMIENTO":
            prioridad = 100
            if pista_ocupada(pista_id) is None:
                messagebox.showerror("Error", "La pista no existe.")
                return
            if not marcar_pista_mantenimiento(pista_id):
                messagebox.showerror("Error", "No se pudo marcar la pista en mantenimiento.")
                return
            avion_id = None
            piloto_id = None
            if not descripcion:
                descripcion = f"Mantenimiento de la pista {pista_id}"
        else:
            estado_pista = pista_ocupada(pista_id)
            if estado_pista is None:
                messagebox.showerror("Error", "La pista no existe.")
                return
            if estado_pista:
                messagebox.showerror("Error", "La pista ya está ocupada o en mantenimiento.")
                return
            if not avion_id or not piloto_id:
                messagebox.showerror("Error", "Avión y piloto son obligatorios para este tipo.")
                return
            estado_avion = avion_ocupado(avion_id)
            if estado_avion is None:
                messagebox.showerror("Error", "El avión no existe.")
                return
            if estado_avion:
                messagebox.showerror("Error", "El avión ya está ocupado.")
                return
            estado_piloto = piloto_ocupado(piloto_id)
            if estado_piloto is None:
                messagebox.showerror("Error", "El piloto no existe.")
                return
            if estado_piloto:
                messagebox.showerror("Error", "El piloto ya está ocupado.")
                return
            avion_tipo = (tipo_avion(avion_id) or "").strip().lower()
            piloto_tipo = (tipo_piloto(piloto_id) or "").strip().lower()
            if avion_tipo != piloto_tipo:
                messagebox.showerror("Error", "El piloto no puede volar este tipo de avión.")
                return
            if avion_tipo == "militar":
                prioridad = 500
            elif avion_tipo == "privado":
                prioridad = 300
            elif avion_tipo == "comercial":
                prioridad = 250
            else:
                prioridad = 100
            if avion_id in ("AL2_01", "AL2_02"):
                prioridad = 1000
            if not descripcion:
                messagebox.showerror("Error", "Ingrese una descripción.")
                return

        if not marcar_pista_ocupada(pista_id):
            self.log("Advertencia: no se pudo marcar la pista como ocupada.")
        if avion_id:
            marcar_avion_ocupado(avion_id)
        if piloto_id:
            marcar_piloto_ocupado(piloto_id)

        msg = create_event(ID, tiempo, avion_id, piloto_id, pista_id, tipo, duracion, descripcion, prioridad)
        if not isinstance(msg, str) or not msg.startswith("Event:"):
            messagebox.showerror("Error", str(msg))
            return

        save_events_json()
        save_airstrips_json()
        save_airplanes_json()
        save_pilots_json()
        self.log(str(msg))
        self._refresh_eventos_tree()
        messagebox.showinfo("OK", "Evento creado y datos guardados.")

    # ——— Flota ———
    def _build_tab_flota(self, nb: ttk.Notebook) -> None:
        f = ttk.Frame(nb, padding=8)
        nb.add(f, text="Flota")

        sub = ttk.Notebook(f)
        sub.pack(fill=tk.BOTH, expand=True)

        # Aviones
        a = ttk.Frame(sub, padding=8)
        sub.add(a, text="Aviones")
        ttk.Label(a, text="ID (máx. 12):").grid(row=0, column=0, sticky=tk.W)
        self._pl_id = tk.StringVar()
        ttk.Entry(a, textvariable=self._pl_id, width=14).grid(row=0, column=1, padx=4)
        ttk.Label(a, text="Tipo (comercial, militar, carga, privado):").grid(row=1, column=0, sticky=tk.W)
        self._pl_tipo = tk.StringVar()
        ttk.Entry(a, textvariable=self._pl_tipo, width=20).grid(row=1, column=1, padx=4)
        ttk.Button(a, text="Agregar avión", command=self._cmd_add_plane).grid(row=2, column=1, sticky=tk.W, pady=6)
        self._tree_pl = ttk.Treeview(a, columns=("id", "tipo", "estado", "piloto"), show="headings", height=8)
        for c, w in zip(("id", "tipo", "estado", "piloto"), (100, 120, 100, 100)):
            self._tree_pl.heading(c, text=c)
            self._tree_pl.column(c, width=w)
        self._tree_pl.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=8)
        a.rowconfigure(3, weight=1)
        a.columnconfigure(1, weight=1)
        ttk.Button(a, text="Refrescar / Guardar JSON", command=self._refresh_planes_save).grid(row=4, column=1, sticky=tk.W)

        # Pilotos
        p = ttk.Frame(sub, padding=8)
        sub.add(p, text="Pilotos")
        ttk.Label(p, text="ID:").grid(row=0, column=0, sticky=tk.W)
        self._pi_id = tk.StringVar()
        ttk.Entry(p, textvariable=self._pi_id, width=12).grid(row=0, column=1, padx=4)
        ttk.Label(p, text="Nombre:").grid(row=1, column=0, sticky=tk.W)
        self._pi_nom = tk.StringVar()
        ttk.Entry(p, textvariable=self._pi_nom, width=16).grid(row=1, column=1, padx=4)
        ttk.Label(p, text="Apellido:").grid(row=2, column=0, sticky=tk.W)
        self._pi_ape = tk.StringVar()
        ttk.Entry(p, textvariable=self._pi_ape, width=16).grid(row=2, column=1, padx=4)
        ttk.Label(p, text="Tipo avión:").grid(row=3, column=0, sticky=tk.W)
        self._pi_tipo = tk.StringVar()
        ttk.Entry(p, textvariable=self._pi_tipo, width=16).grid(row=3, column=1, padx=4)
        ttk.Button(p, text="Agregar piloto", command=self._cmd_add_pilot).grid(row=4, column=1, sticky=tk.W, pady=6)
        self._tree_pi = ttk.Treeview(p, columns=("id", "nombre", "tipo", "estado"), show="headings", height=8)
        for c, w in zip(("id", "nombre", "tipo", "estado"), (80, 160, 100, 90)):
            self._tree_pi.heading(c, text=c)
            self._tree_pi.column(c, width=w)
        self._tree_pi.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=8)
        p.rowconfigure(5, weight=1)
        ttk.Button(p, text="Refrescar / Guardar JSON", command=self._refresh_pilots_save).grid(row=6, column=1, sticky=tk.W)

        # Pistas
        s = ttk.Frame(sub, padding=8)
        sub.add(s, text="Pistas")
        ttk.Label(s, text="ID pista:").grid(row=0, column=0, sticky=tk.W)
        self._as_id = tk.StringVar()
        ttk.Entry(s, textvariable=self._as_id, width=14).grid(row=0, column=1, padx=4)
        ttk.Button(s, text="Agregar pista", command=self._cmd_add_strip).grid(row=1, column=1, sticky=tk.W, pady=6)
        self._tree_as = ttk.Treeview(s, columns=("id", "callsign", "estado"), show="headings", height=8)
        for c, w in zip(("id", "callsign", "estado"), (100, 120, 100)):
            self._tree_as.heading(c, text=c)
            self._tree_as.column(c, width=w)
        self._tree_as.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=8)
        s.rowconfigure(2, weight=1)
        ttk.Button(s, text="Refrescar / Guardar JSON", command=self._refresh_strips_save).grid(row=3, column=1, sticky=tk.W)

        self._refresh_planes_tree()
        self._refresh_pilots_tree()
        self._refresh_strips_tree()

    def _refresh_planes_tree(self) -> None:
        for i in self._tree_pl.get_children():
            self._tree_pl.delete(i)
        for pid, d in airplanes_map.items():
            self._tree_pl.insert(
                "",
                tk.END,
                values=(pid, d.get("airplane_type", ""), d.get("status", ""), d.get("pilot_id") or ""),
            )

    def _refresh_pilots_tree(self) -> None:
        for i in self._tree_pi.get_children():
            self._tree_pi.delete(i)
        for pid, d in pilots_map.items():
            nom = f"{d.get('first_name', '')} {d.get('last_name', '')}"
            self._tree_pi.insert(
                "",
                tk.END,
                values=(pid, nom.strip(), d.get("airplane_type", ""), d.get("status", "")),
            )

    def _refresh_strips_tree(self) -> None:
        for i in self._tree_as.get_children():
            self._tree_as.delete(i)
        for aid, d in airstrip_map.items():
            self._tree_as.insert(
                "",
                tk.END,
                values=(aid, d.get("callsign", ""), d.get("status", "")),
            )

    def _cmd_add_plane(self) -> None:
        r = add_airplane(self._pl_id.get(), self._pl_tipo.get())
        if r:
            self.log(str(r))
            if "has been added" in str(r):
                save_airplanes_json()
                self._refresh_planes_tree()
        else:
            messagebox.showwarning("Avión", "No se agregó (ID vacío, duplicado o tipo inválido).")

    def _refresh_planes_save(self) -> None:
        save_airplanes_json()
        self._refresh_planes_tree()
        messagebox.showinfo("OK", "Aviones guardados.")

    def _cmd_add_pilot(self) -> None:
        r = add_pilot(self._pi_id.get(), self._pi_nom.get(), self._pi_ape.get(), self._pi_tipo.get())
        if r:
            self.log(str(r))
            if "has been added" in str(r):
                save_pilots_json()
                self._refresh_pilots_tree()
        else:
            messagebox.showwarning("Piloto", "No se agregó (revise campos y tipo de avión).")

    def _refresh_pilots_save(self) -> None:
        save_pilots_json()
        self._refresh_pilots_tree()
        messagebox.showinfo("OK", "Pilotos guardados.")

    def _cmd_add_strip(self) -> None:
        r = add_airstrip(self._as_id.get().strip(), None)
        self.log(str(r))
        save_airstrips_json()
        self._refresh_strips_tree()

    def _refresh_strips_save(self) -> None:
        save_airstrips_json()
        self._refresh_strips_tree()
        messagebox.showinfo("OK", "Pistas guardadas.")

    # ——— Simulación ———
    def _build_tab_simulacion(self, nb: ttk.Notebook) -> None:
        f = ttk.Frame(nb, padding=10)
        nb.add(f, text="Simulación")

        ttk.Label(f, text="Simulación parcial: tiempo máximo").grid(row=0, column=0, sticky=tk.W)
        self._sim_tmax = tk.StringVar(value="100")
        ttk.Entry(f, textvariable=self._sim_tmax, width=12).grid(row=0, column=1, padx=6)
        self._sim_del = tk.BooleanVar(value=False)
        ttk.Checkbutton(f, text="Eliminar eventos simulados del calendario", variable=self._sim_del).grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=4
        )
        ttk.Button(f, text="Ejecutar simulación parcial", command=self._cmd_sim_parcial).grid(
            row=2, column=0, columnspan=2, sticky=tk.W, pady=8
        )

        ttk.Separator(f, orient=tk.HORIZONTAL).grid(row=3, column=0, columnspan=2, sticky="ew", pady=12)
        ttk.Label(
            f,
            text="Calendario completo: puede tardar (pausas internas). Se ejecuta en segundo plano.",
        ).grid(row=4, column=0, columnspan=2, sticky=tk.W)
        ttk.Button(f, text="Simular calendario completo", command=self._cmd_sim_full).grid(
            row=5, column=0, columnspan=2, sticky=tk.W, pady=6
        )

        ttk.Separator(f, orient=tk.HORIZONTAL).grid(row=6, column=0, columnspan=2, sticky="ew", pady=12)
        ttk.Button(f, text="Simular siguiente evento", command=self._cmd_sim_next).grid(row=7, column=0, sticky=tk.W, pady=4)
        self._sim_del_next = tk.BooleanVar(value=True)
        ttk.Checkbutton(f, text="Eliminar ese evento del calendario tras simular", variable=self._sim_del_next).grid(
            row=8, column=0, columnspan=2, sticky=tk.W
        )

        ttk.Label(f, text="Varios seguidos (número):").grid(row=9, column=0, sticky=tk.W, pady=(12, 0))
        self._sim_n = tk.StringVar(value="3")
        ttk.Entry(f, textvariable=self._sim_n, width=6).grid(row=9, column=1, sticky=tk.W, padx=6, pady=(12, 0))
        ttk.Button(f, text="Ejecutar N siguientes", command=self._cmd_sim_n).grid(row=10, column=0, sticky=tk.W, pady=6)

    def _cmd_sim_parcial(self) -> None:
        try:
            tmax = float(self._sim_tmax.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Error", "Tiempo máximo inválido.")
            return
        if tmax < 0:
            messagebox.showerror("Error", "El tiempo debe ser positivo.")
            return

        def work():
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                try:
                    simular_por_tiempo(
                        tmax,
                        eliminar_simulados=self._sim_del.get(),
                        pedir_confirmacion_eliminar=False,
                    )
                except Exception as e:
                    buf.write(f"\nError: {e}\n")
            text = buf.getvalue()
            self.after(0, lambda: self._sim_done(text))

        self.config(cursor="watch")
        threading.Thread(target=work, daemon=True).start()

    def _cmd_sim_full(self) -> None:
        def work():
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                try:
                    simular_calendario()
                except Exception as e:
                    buf.write(f"\nError: {e}\n")
            text = buf.getvalue()
            self.after(0, lambda: self._sim_done(text))

        self.config(cursor="watch")
        threading.Thread(target=work, daemon=True).start()

    def _sim_done(self, text: str) -> None:
        self.config(cursor="")
        self.log(text)
        self._refresh_tiempo_label()
        self._refresh_eventos_tree()
        messagebox.showinfo("Simulación", "Simulación finalizada. Revise la pestaña Consola.")

    def _cmd_sim_next(self) -> None:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ev = simular_siguiente_evento()
        self.log(buf.getvalue())
        self._refresh_tiempo_label()
        if ev and self._sim_del_next.get():
            if delete_event_by_id(ev.id):
                self.log(f"Evento {ev.id} eliminado del calendario.")
        self._refresh_eventos_tree()

    def _cmd_sim_n(self) -> None:
        try:
            n = int(self._sim_n.get())
        except ValueError:
            messagebox.showerror("Error", "N debe ser entero.")
            return
        for i in range(n):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                ev = simular_siguiente_evento()
            self.log(buf.getvalue())
            if ev is None:
                self.log("No hay más eventos.")
                break
        self._refresh_tiempo_label()
        self._refresh_eventos_tree()

    def _on_close(self) -> None:
        try:
            save_events_json()
            save_airstrips_json()
            save_airplanes_json()
            save_pilots_json()
        except OSError as e:
            messagebox.showwarning("Guardar", f"No se pudo guardar todo: {e}")
        self.destroy()


def run_app() -> None:
    app = TorreControlGUI()
    app.mainloop()


if __name__ == "__main__":
    run_app()
