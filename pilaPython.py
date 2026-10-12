import tkinter as tk


# ----------------------------------------------------------------------
# Lógica de la Pila
# ----------------------------------------------------------------------
class Pila:
    def __init__(self, capacidad=8):
        self.capacidad = capacidad
        self._datos = []

    def apilar(self, valor):          # push
        if self.esta_llena():
            raise OverflowError("Desbordamiento (overflow): la pila está llena")
        self._datos.append(valor)

    def desapilar(self):              # pop
        if self.esta_vacia():
            raise IndexError("Subdesbordamiento (underflow): la pila está vacía")
        return self._datos.pop()

    def cima(self):                   # peek / top
        if self.esta_vacia():
            raise IndexError("La pila está vacía, no hay cima")
        return self._datos[-1]

    def esta_vacia(self):
        return len(self._datos) == 0

    def esta_llena(self):
        return len(self._datos) >= self.capacidad

    def tamano(self):
        return len(self._datos)


# ----------------------------------------------------------------------
# Interfaz gráfica
# ----------------------------------------------------------------------
class AppPila:
    CAPACIDAD = 8
    ALTO = 40            # alto de cada bloque
    SEP = 4              # separación entre bloques
    ANCHO = 160          # ancho de cada bloque
    X0 = 110             # x izquierda de los bloques
    BASE_Y = 440         # y del fondo de la pila
    Y_ENTRADA = 25       # y desde donde entran / salen los bloques
    COLORES = ["#4F8EF7", "#F76C6C", "#4CC38A", "#F7B84F",
               "#A56EF7", "#2EC4C4", "#F78FB3", "#8FB339"]

    def __init__(self, root):
        self.root = root
        root.title("Pila (Stack) - Visualización gráfica")
        root.configure(bg="#1E2230")
        root.resizable(False, False)

        self.pila = Pila(self.CAPACIDAD)
        self.bloques = []          # lista de (rect_id, texto_id)
        self.contador_color = 0
        self.ocupado = False       # True mientras hay una animación

        self._crear_widgets()
        self._dibujar_contenedor()
        self._actualizar_estado()
        self._log("Pila creada. Capacidad máxima: %d elementos." % self.CAPACIDAD)

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _crear_widgets(self):
        # Canvas (zona de dibujo)
        self.canvas = tk.Canvas(self.root, width=380, height=480,
                                bg="#262B3D", highlightthickness=0)
        self.canvas.grid(row=0, column=0, rowspan=2, padx=15, pady=15)

        # Panel derecho
        panel = tk.Frame(self.root, bg="#1E2230")
        panel.grid(row=0, column=1, sticky="n", padx=(0, 15), pady=15)

        tk.Label(panel, text="PILA (LIFO)", font=("Arial", 18, "bold"),
                 fg="white", bg="#1E2230").pack(anchor="w")
        tk.Label(panel, text="El último en entrar es el primero en salir",
                 font=("Arial", 9), fg="#9AA3BF", bg="#1E2230").pack(anchor="w", pady=(0, 12))

        tk.Label(panel, text="Valor a apilar:", fg="white", bg="#1E2230",
                 font=("Arial", 10)).pack(anchor="w")
        self.entrada = tk.Entry(panel, font=("Arial", 14), width=14, justify="center")
        self.entrada.pack(anchor="w", pady=(2, 10))
        self.entrada.bind("<Return>", lambda e: self.apilar())
        self.entrada.focus()

        def boton(texto, color, comando):
            b = tk.Button(panel, text=texto, command=comando, bg=color, fg="white",
                          activebackground=color, font=("Arial", 11, "bold"),
                          relief="flat", width=22, pady=5, cursor="hand2")
            b.pack(anchor="w", pady=3)
            return b

        self.botones = [
            boton("⬇  Apilar (push)", "#4CC38A", self.apilar),
            boton("⬆  Desapilar (pop)", "#F76C6C", self.desapilar),
            boton("👁  Ver cima (peek)", "#4F8EF7", self.ver_cima),
            boton("🗑  Vaciar pila", "#7A7F94", self.vaciar),
        ]

        # Estado
        self.lbl_estado = tk.Label(panel, text="", justify="left", fg="#E6E9F5",
                                   bg="#1E2230", font=("Consolas", 10))
        self.lbl_estado.pack(anchor="w", pady=(12, 6))

        # Registro de operaciones
        tk.Label(panel, text="Registro de operaciones:", fg="white", bg="#1E2230",
                 font=("Arial", 10)).pack(anchor="w")
        marco_log = tk.Frame(panel)
        marco_log.pack(anchor="w")
        self.log_txt = tk.Text(marco_log, width=34, height=9, bg="#12151F",
                               fg="#B8C0DC", font=("Consolas", 9), state="disabled",
                               relief="flat", wrap="word")
        scroll = tk.Scrollbar(marco_log, command=self.log_txt.yview)
        self.log_txt.configure(yscrollcommand=scroll.set)
        self.log_txt.pack(side="left")
        scroll.pack(side="right", fill="y")
        self.log_txt.tag_config("ok", foreground="#4CC38A")
        self.log_txt.tag_config("error", foreground="#F76C6C")
        self.log_txt.tag_config("info", foreground="#7FB2FF")

    # ------------------------------------------------------------------
    # Dibujo
    # ------------------------------------------------------------------
    def _y_slot(self, indice):
        """Coordenada y superior del bloque en la posición 'indice' (0 = fondo)."""
        return self.BASE_Y - (indice + 1) * (self.ALTO + self.SEP)

    def _dibujar_contenedor(self):
        c = self.canvas
        izq, der = self.X0 - 12, self.X0 + self.ANCHO + 12
        tope = self._y_slot(self.CAPACIDAD - 1) - 8
        c.create_line(izq, tope, izq, self.BASE_Y + 4, width=5, fill="#C9CEE3", capstyle="round")
        c.create_line(der, tope, der, self.BASE_Y + 4, width=5, fill="#C9CEE3", capstyle="round")
        c.create_line(izq, self.BASE_Y + 4, der, self.BASE_Y + 4, width=5,
                      fill="#C9CEE3", capstyle="round")
        c.create_text(self.X0 + self.ANCHO / 2, self.BASE_Y + 24, text="FONDO",
                      fill="#7A7F94", font=("Arial", 9, "bold"))
        c.create_text(self.X0 + self.ANCHO / 2, 8, text="↓ entrada / salida ↑",
                      fill="#7A7F94", font=("Arial", 8))

    def _crear_bloque(self, valor, y):
        color = self.COLORES[self.contador_color % len(self.COLORES)]
        self.contador_color += 1
        x1 = self.X0 + self.ANCHO
        rect = self.canvas.create_rectangle(self.X0, y, x1, y + self.ALTO, fill=color,
                                            outline="white", width=2)
        texto = self.canvas.create_text((self.X0 + x1) / 2, y + self.ALTO / 2, text=str(valor),
                                        fill="white", font=("Arial", 14, "bold"))
        return rect, texto

    def _dibujar_puntero(self):
        self.canvas.delete("puntero")
        if self.pila.esta_vacia():
            return
        y = self._y_slot(self.pila.tamano() - 1) + self.ALTO / 2
        x = self.X0 + self.ANCHO + 22
        self.canvas.create_line(x + 55, y, x + 2, y, arrow="last", width=3,
                                fill="#FFD166", tags="puntero")
        self.canvas.create_text(x + 80, y, text="CIMA", fill="#FFD166",
                                font=("Arial", 11, "bold"), tags="puntero")

    # ------------------------------------------------------------------
    # Animación
    # ------------------------------------------------------------------
    def _mover(self, items, dy, al_terminar, pasos=22, ms=14):
        paso = dy / pasos

        def frame(n):
            if n == 0:
                al_terminar()
                return
            for it in items:
                self.canvas.move(it, 0, paso)
            self.root.after(ms, lambda: frame(n - 1))

        frame(pasos)

    def _bloquear(self, estado):
        self.ocupado = estado
        for b in self.botones:
            b.config(state="disabled" if estado else "normal")

    # ------------------------------------------------------------------
    # Operaciones
    # ------------------------------------------------------------------
    def apilar(self):
        if self.ocupado:
            return
        valor = self.entrada.get().strip()
        if not valor:
            self._log("Escribe un valor para apilar.", "error")
            return
        try:
            self.pila.apilar(valor)
        except OverflowError as e:
            self._log(str(e), "error")
            self._parpadear_contenedor()
            return

        self._bloquear(True)
        destino = self._y_slot(self.pila.tamano() - 1)
        rect, texto = self._crear_bloque(valor, self.Y_ENTRADA)

        def fin():
            self.bloques.append((rect, texto))
            self._dibujar_puntero()
            self._actualizar_estado()
            self._log("push('%s')  →  tamaño = %d" % (valor, self.pila.tamano()), "ok")
            self.entrada.delete(0, "end")
            self._bloquear(False)
            self.entrada.focus()

        self._mover((rect, texto), destino - self.Y_ENTRADA, fin)

    def desapilar(self):
        if self.ocupado:
            return
        try:
            valor = self.pila.desapilar()
        except IndexError as e:
            self._log(str(e), "error")
            return

        self._bloquear(True)
        rect, texto = self.bloques.pop()
        self.canvas.delete("puntero")
        y_actual = self.canvas.coords(rect)[1]

        def fin():
            self.canvas.delete(rect)
            self.canvas.delete(texto)
            self._dibujar_puntero()
            self._actualizar_estado()
            self._log("pop()  →  salió '%s'  |  tamaño = %d" % (valor, self.pila.tamano()), "ok")
            self._bloquear(False)

        self._mover((rect, texto), self.Y_ENTRADA - y_actual, fin)

    def ver_cima(self):
        if self.ocupado:
            return
        try:
            valor = self.pila.cima()
        except IndexError as e:
            self._log(str(e), "error")
            return
        self._log("peek()  →  la cima es '%s' (no se elimina)" % valor, "info")
        rect = self.bloques[-1][0]
        self._bloquear(True)

        def parpadeo(n):
            if n == 0:
                self.canvas.itemconfig(rect, outline="white", width=2)
                self._bloquear(False)
                return
            if n % 2 == 0:
                self.canvas.itemconfig(rect, outline="#FFD166", width=5)
            else:
                self.canvas.itemconfig(rect, outline="white", width=2)
            self.root.after(180, lambda: parpadeo(n - 1))

        parpadeo(6)

    def vaciar(self):
        if self.ocupado:
            return
        for rect, texto in self.bloques:
            self.canvas.delete(rect)
            self.canvas.delete(texto)
        self.bloques.clear()
        self.pila = Pila(self.CAPACIDAD)
        self._dibujar_puntero()
        self._actualizar_estado()
        self._log("La pila se ha vaciado.", "info")

    # ------------------------------------------------------------------
    # Utilidades de interfaz
    # ------------------------------------------------------------------
    def _parpadear_contenedor(self):
        self._bloquear(True)

        def parpadeo(n):
            if n == 0:
                self.canvas.config(bg="#262B3D")
                self._bloquear(False)
                return
            self.canvas.config(bg="#5A2A33" if n % 2 == 0 else "#262B3D")
            self.root.after(120, lambda: parpadeo(n - 1))

        parpadeo(6)

    def _actualizar_estado(self):
        p = self.pila
        cima = p.cima() if not p.esta_vacia() else "—"
        self.lbl_estado.config(
            text="Tamaño : %d / %d\nVacía  : %s\nLlena  : %s\nCima   : %s" % (
                p.tamano(), p.capacidad,
                "Sí" if p.esta_vacia() else "No",
                "Sí" if p.esta_llena() else "No",
                cima))

    def _log(self, mensaje, etiqueta="info"):
        self.log_txt.config(state="normal")
        self.log_txt.insert("end", "• " + mensaje + "\n", etiqueta)
        self.log_txt.see("end")
        self.log_txt.config(state="disabled")


if __name__ == "__main__":
    ventana = tk.Tk()
    AppPila(ventana)
    ventana.mainloop()