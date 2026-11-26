"""Interfaz gráfica (Tkinter): paleta, pincel, área, guardar/cargar y simulación."""
import tkinter as tk
from tkinter import messagebox, filedialog

from constantes import *
from colores import PALETA, COLOR_BASE, texto_para
from mundo import Mundo
import archivos

HERRAMIENTAS = [
    ("Arena", ARENA), ("Agua", AGUA), ("Piedra", PIEDRA),
    ("Tierra", TIERRA), ("Fuego", FUEGO), ("Semilla", SEMILLA),
    ("Planta", PLANTA_1), ("Animal", ANIMAL), ("Borrador", AIRE),
]


class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sandbox de Elementos")
        self.resizable(False, False)

        self.mundo = Mundo(N_INICIAL)
        self.elemento = ARENA
        self.pausado = False
        self.tick = 0
        self.ultimo = None
        self.inicio_area = None
        self.id_area = None

        self.modo = tk.StringVar(value="pincel")
        self.tam_pincel = tk.IntVar(value=2)
        self.retardo = tk.IntVar(value=60)
        self.var_n = tk.StringVar(value=str(N_INICIAL))
        self.estado = tk.StringVar()
        self.botones = {}

        self._crear_panel()
        self._crear_lienzo()
        self._seleccionar(ARENA)
        self._ciclo()

    # ------------------------------------------------------------ interfaz
    def _crear_panel(self):
        panel = tk.Frame(self, padx=8, pady=8)
        panel.grid(row=0, column=0, sticky="ns")

        marco = tk.LabelFrame(panel, text="Elementos", padx=4, pady=4)
        marco.pack(fill="x")
        for i, (nombre, cod) in enumerate(HERRAMIENTAS):
            color = COLOR_BASE[cod]
            b = tk.Button(marco, text=nombre, width=9, bg=color, fg=texto_para(color),
                          activebackground=color, command=lambda c=cod: self._seleccionar(c))
            b.grid(row=i // 2, column=i % 2, padx=2, pady=2)
            self.botones[cod] = b

        marco = tk.LabelFrame(panel, text="Herramienta", padx=4, pady=4)
        marco.pack(fill="x", pady=4)
        tk.Radiobutton(marco, text="Pincel (arrastrar)", variable=self.modo,
                       value="pincel").pack(anchor="w")
        tk.Radiobutton(marco, text="Área rectangular", variable=self.modo,
                       value="area").pack(anchor="w")
        tk.Label(marco, text="Tamaño del pincel (celdas)").pack(anchor="w")
        tk.Scale(marco, from_=1, to=10, orient="horizontal",
                 variable=self.tam_pincel, command=lambda _: self._actualizar_estado()
                 ).pack(fill="x")

        marco = tk.LabelFrame(panel, text="Mundo (N × N)", padx=4, pady=4)
        marco.pack(fill="x")
        tk.Spinbox(marco, from_=N_MIN, to=N_MAX, width=5, textvariable=self.var_n
                   ).pack(side="left", padx=2)
        tk.Button(marco, text="Aplicar N", command=self._aplicar_n).pack(side="left", padx=2)

        marco = tk.LabelFrame(panel, text="Simulación", padx=4, pady=4)
        marco.pack(fill="x", pady=4)
        self.btn_pausa = tk.Button(marco, text="Pausar", command=self._alternar_pausa)
        self.btn_pausa.pack(fill="x")
        tk.Label(marco, text="Retardo por paso (ms)").pack(anchor="w")
        tk.Scale(marco, from_=10, to=300, orient="horizontal",
                 variable=self.retardo).pack(fill="x")

        marco = tk.LabelFrame(panel, text="Mapa", padx=4, pady=4)
        marco.pack(fill="x")
        tk.Button(marco, text="Guardar mapa", command=self._guardar).pack(fill="x", pady=1)
        tk.Button(marco, text="Cargar mapa", command=self._cargar).pack(fill="x", pady=1)
        tk.Button(marco, text="Limpiar mapa", command=self._limpiar).pack(fill="x", pady=1)

        tk.Label(self, textvariable=self.estado, anchor="w", relief="sunken"
                 ).grid(row=1, column=0, columnspan=2, sticky="we")

    def _crear_lienzo(self):
        n = self.mundo.n
        self.cel = max(3, TAM_LIENZO // n)
        if not hasattr(self, "lienzo"):
            self.lienzo = tk.Canvas(self, highlightthickness=0)
            self.lienzo.grid(row=0, column=1)
            self.lienzo.bind("<ButtonPress-1>", self._presionar)
            self.lienzo.bind("<B1-Motion>", self._arrastrar)
            self.lienzo.bind("<ButtonRelease-1>", self._soltar)
            self.lienzo.bind("<ButtonPress-3>", lambda e: self._borrar_click(e, True))
            self.lienzo.bind("<B3-Motion>", lambda e: self._borrar_click(e, False))
            self.lienzo.bind("<Motion>", self._mover_cursor)
            self.lienzo.bind("<Leave>", lambda e: self.lienzo.delete("cursor"))
        self.lienzo.config(width=n * self.cel, height=n * self.cel)
        self.lienzo.delete("all")
        self.imagen = tk.PhotoImage(width=n, height=n)
        self.imagen_zoom = None
        self.id_imagen = self.lienzo.create_image(0, 0, anchor="nw")
        self.var_n.set(str(n))

    def _actualizar_estado(self):
        self.estado.set(f"Elemento: {NOMBRES[self.elemento] if self.elemento != PLANTA_1 else 'Planta'}"
                        f"  |  Pincel: {self.tam_pincel.get()}x{self.tam_pincel.get()}"
                        f"  |  Mundo: {self.mundo.n}x{self.mundo.n}"
                        f"  |  Clic izquierdo: dibujar · Clic derecho: borrar")

    def _seleccionar(self, cod):
        self.elemento = cod
        for c, b in self.botones.items():
            b.config(relief="sunken" if c == cod else "raised", bd=4 if c == cod else 2)
        self._actualizar_estado()

    # ------------------------------------------------------------- dibujo
    def _dibujar(self):
        m, n, t = self.mundo.matriz, self.mundo.n, self.tick
        filas = []
        for f in range(n):
            fila = m[f]
            filas.append("{" + " ".join(
                PALETA[fila[c]][(f * 31 + c * 17 + (t if fila[c] == FUEGO else 0)) % 3]
                for c in range(n)) + "}")
        self.imagen.put(" ".join(filas))
        self.imagen_zoom = self.imagen.zoom(self.cel)
        self.lienzo.itemconfig(self.id_imagen, image=self.imagen_zoom)

    def _ciclo(self):
        if not self.pausado:
            self.mundo.simular_paso()
            self.tick += 1
        self._dibujar()
        self.after(self.retardo.get(), self._ciclo)

    # -------------------------------------------------------------- mouse
    def _celda(self, e):
        n = self.mundo.n
        return (min(max(e.y // self.cel, 0), n - 1), min(max(e.x // self.cel, 0), n - 1))

    def _rango_pincel(self, f, c):
        s = self.tam_pincel.get()
        f0, c0 = f - s // 2, c - s // 2
        return range(f0, f0 + s), range(c0, c0 + s)

    def _pintar(self, f, c, codigo, primera):
        if codigo == ANIMAL:                 # un animal por clic
            if primera:
                self.mundo.colocar(f, c, ANIMAL)
            return
        filas, cols = self._rango_pincel(f, c)
        for ff in filas:
            for cc in cols:
                self.mundo.colocar(ff, cc, codigo)

    def _linea(self, a, b, codigo):
        (f0, c0), (f1, c1) = a, b
        pasos = max(abs(f1 - f0), abs(c1 - c0), 1)
        for i in range(pasos + 1):
            self._pintar(round(f0 + (f1 - f0) * i / pasos),
                         round(c0 + (c1 - c0) * i / pasos), codigo, False)

    def _presionar(self, e):
        f, c = self._celda(e)
        if self.modo.get() == "pincel":
            self.ultimo = (f, c)
            self._pintar(f, c, self.elemento, True)
        else:
            self.inicio_area = (f, c)
            self.id_area = self.lienzo.create_rectangle(0, 0, 0, 0, outline="white", width=2, dash=(4, 2))
            self._rect_area(f, c)

    def _arrastrar(self, e):
        f, c = self._celda(e)
        if self.modo.get() == "pincel" and self.ultimo:
            self._linea(self.ultimo, (f, c), self.elemento)
            self.ultimo = (f, c)
        elif self.inicio_area:
            self._rect_area(f, c)
        self._mover_cursor(e)

    def _soltar(self, e):
        if self.modo.get() == "area" and self.inicio_area:
            f, c = self._celda(e)
            f0, c0 = self.inicio_area
            fa, fb, ca, cb = min(f0, f), max(f0, f), min(c0, c), max(c0, c)
            if self.elemento == ANIMAL:
                self.mundo.colocar(fb, ca, ANIMAL)
            else:
                for ff in range(fa, fb + 1):
                    for cc in range(ca, cb + 1):
                        self.mundo.colocar(ff, cc, self.elemento)
            self.lienzo.delete(self.id_area)
            self.inicio_area = None
        self.ultimo = None

    def _rect_area(self, f, c):
        f0, c0 = self.inicio_area
        k = self.cel
        self.lienzo.coords(self.id_area, min(c0, c) * k, min(f0, f) * k,
                           (max(c0, c) + 1) * k, (max(f0, f) + 1) * k)

    def _borrar_click(self, e, primera):
        f, c = self._celda(e)
        if primera:
            self.ultimo_borrado = (f, c)
        self._linea(getattr(self, "ultimo_borrado", (f, c)), (f, c), AIRE)
        self.ultimo_borrado = (f, c)

    def _mover_cursor(self, e):
        self.lienzo.delete("cursor")
        if self.modo.get() != "pincel":
            return
        f, c = self._celda(e)
        filas, cols = self._rango_pincel(f, c)
        k = self.cel
        self.lienzo.create_rectangle(cols[0] * k, filas[0] * k, (cols[-1] + 1) * k,
                                     (filas[-1] + 1) * k, outline="white", tags="cursor")

    # ------------------------------------------------------------ botones
    def _alternar_pausa(self):
        self.pausado = not self.pausado
        self.btn_pausa.config(text="Reanudar" if self.pausado else "Pausar")

    def _aplicar_n(self):
        try:
            n = int(self.var_n.get())
            if not (N_MIN <= n <= N_MAX):
                raise ValueError
        except ValueError:
            messagebox.showerror("N inválido", f"N debe ser un entero entre {N_MIN} y {N_MAX}.")
            self.var_n.set(str(self.mundo.n))
            return
        if n != self.mundo.n:
            if not messagebox.askyesno("Cambiar N", "Cambiar N reinicia el mundo. ¿Continuar?"):
                self.var_n.set(str(self.mundo.n))
                return
            self.mundo = Mundo(n)
            self._crear_lienzo()
            self._actualizar_estado()

    def _guardar(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("Mapa JSON", "*.json")])
        if not ruta:
            return
        try:
            archivos.guardar_mapa(self.mundo, ruta)
            messagebox.showinfo("Guardar mapa", "Mapa guardado correctamente.")
        except OSError as e:
            messagebox.showerror("Error al guardar", str(e))

    def _cargar(self):
        ruta = filedialog.askopenfilename(filetypes=[("Mapa JSON", "*.json"), ("Todos", "*.*")])
        if not ruta:
            return
        try:
            nuevo = archivos.cargar_mapa(ruta)
        except archivos.ArchivoInvalido as e:
            messagebox.showerror("Archivo inválido", str(e))
            return
        cambio = nuevo.n != self.mundo.n
        self.mundo = nuevo
        if cambio:
            self._crear_lienzo()
        self.var_n.set(str(self.mundo.n))
        self._actualizar_estado()

    def _limpiar(self):
        if messagebox.askyesno("Limpiar mapa", "¿Restablecer todas las casillas a aire?"):
            self.mundo.limpiar()
