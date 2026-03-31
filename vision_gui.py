# ======================================================================================
# --------------------------------------------------------------------------------------
# INTERFAZ QUE APLICA ANÁLISIS DE CONTORNOS EN IMÁGENES BINARIAS
# Elaborado por:
# Cristina
# Jessica Victoria Martínez Medina
# --------------------------------------------------------------------------------------
# ======================================================================================


# ===============================================
# BIBLIOTECAS NECESARIAS
# ===============================================
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
from tkinter import messagebox
import cv2
import numpy as np
from collections import Counter
import pandas as pd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import heapq
import math

# ===============================================
# APLICACIÓN
# ===============================================
class App:
    """
    Aplicación gráfica para el análisis de contornos en imágenes binarias.

    Flujo general del sistema:
    1. Cargar imagen, binarizar
    2. Detectar contorno
    3. Generar cadenas (F4, F8, etc.)
    4. Analizar (histograma, entropía, propiedades)
    5. Decodificar
    6. Comprimir (Huffman y Aritmético)
    """
    def __init__(self, root):
        """
        Inicializa toda la interfaz gráfica y estructuras internas.

        Parámetros:
        root (Tk): ventana principal
        """

        self.root = root
        self.root.title("Análisis de Contornos")
        self.root = root
        self.root.title("Análisis de Contornos de imágenes binarias")

        # ===============================================
        # DETALLES DE INTERFAZ
        # ===============================================
        # -----------------------------------------------
        # Menú Superior (Interfaz)
        # -----------------------------------------------
        menubar = tk.Menu(root)

        # Menú Archivo
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menu_archivo.add_command(label="Cargar imagen", command=self.cargar_imagen)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=root.quit)

        menubar.add_cascade(label="Archivo", menu=menu_archivo)

        # Menú Contorno
        menu_contorno = tk.Menu(menubar, tearoff=0)
        menu_contorno.add_command(label="Detectar contorno", command=self.detectar_contorno)

        menubar.add_cascade(label="Contorno", menu=menu_contorno)

        # Menú Cadenas
        menu_cadenas = tk.Menu(menubar, tearoff=0)
        menu_cadenas.add_command(label="F4", command=self.generar_f4)
        menu_cadenas.add_command(label="F8", command=self.generar_f8)
        menu_cadenas.add_command(label="AF8", command=self.generar_af8)
        menu_cadenas.add_command(label="VCC", command=self.generar_vcc)
        menu_cadenas.add_command(label="3OT", command=self.generar_3ot)

        menubar.add_cascade(label="Cadenas", menu=menu_cadenas)

        # Menú Decodificación
        menu_decodificacion = tk.Menu(menubar, tearoff=0)
        menu_decodificacion.add_command(label="F4", command=self.decodificar_f4)
        menu_decodificacion.add_command(label="F8", command=self.decodificar_f8)
        menu_decodificacion.add_command(label="AF8", command=self.decodificar_af8)
        menu_decodificacion.add_command(label="VCC", command=self.decodificar_vcc)
        menu_decodificacion.add_command(label="3OT", command=self.decodificar_3ot)

        menubar.add_cascade(label="Decodificacion", menu=menu_decodificacion)

        # Menú Análisis Histograma y Entropía
        menu_analisis = tk.Menu(menubar, tearoff=0)
        menu_analisis.add_command(label="Histograma", command=self.mostrar_histograma)
        menu_analisis.add_command(label="Entropía", command=self.mostrar_entropia)

        menubar.add_cascade(label="Análisis", menu=menu_analisis)

        # Menú Propiedades Geométricas
        menu_propiedades = tk.Menu(menubar, tearoff=0)

        menu_propiedades.add_command(label="Mostrar propiedades", command=self.mostrar_propiedades)

        menubar.add_cascade(label="Propiedades", menu=menu_propiedades)

        root.config(menu=menubar)

        # Menú Compresion de Huffman y Compresion aritmética
        menu_Comprimir = tk.Menu(menubar, tearoff=0)

        menu_Comprimir.add_command(label="Comprimir", command=self.comprimir)

        menubar.add_cascade(label="Comprimir", menu=menu_Comprimir)
        
        root.config(menu=menubar)

        # -----------------------------------------------
        # Barra de Botones de Cadenas (Interfaz)
        # -----------------------------------------------
        self.frame_cadenas = tk.Frame(root)
        self.frame_cadenas.pack(pady=5)

        self.btn_f4 = tk.Button(self.frame_cadenas, text="F4", width=8, command=self.generar_f4)
        self.btn_f4.pack(side=tk.LEFT, padx=5)

        self.btn_f8 = tk.Button(self.frame_cadenas, text="F8", width=8, command=self.generar_f8)
        self.btn_f8.pack(side=tk.LEFT, padx=5)

        self.btn_af8 = tk.Button(self.frame_cadenas, text="AF8", width=8, command=self.generar_af8)
        self.btn_af8.pack(side=tk.LEFT, padx=5)

        self.btn_vcc = tk.Button(self.frame_cadenas, text="VCC", width=8, command=self.generar_vcc)
        self.btn_vcc.pack(side=tk.LEFT, padx=5)

        self.btn_3ot = tk.Button(self.frame_cadenas, text="3OT", width=8, command=self.generar_3ot)
        self.btn_3ot.pack(side=tk.LEFT, padx=5)

        #-----------------------------------------------
        # Área para hacer el drop de la imagen (Interfaz)
        #-----------------------------------------------
        self.drop_label = tk.Label(root, text="Pegue aquí la imagen binaria del objeto a analizar",
                                   width=50, height=3, bg="lightgray")
        self.drop_label.pack(pady=10)

        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.drop_imagen)

        self.label_img = tk.Label(root)
        self.label_img.pack()

        self.img = None
        self.img_binaria = None

        # -----------------------------------------------
        # Área de Resultados (Interfaz)
        # -----------------------------------------------
        frame_texto = tk.Frame(root)
        frame_texto.pack(fill=tk.BOTH, expand=True, pady=10)

        scrollbar = tk.Scrollbar(frame_texto)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_resultado = tk.Text(frame_texto, height=30, width=70, yscrollcommand=scrollbar.set)
        self.text_resultado.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.text_resultado.yview)

        self.text_resultado.config(font=("Consolas", 10)) # Fuente más clara

        root.configure(bg="#f5f5f5")

        self.frame_cadenas.configure(bg="#f5f5f5")
        self.drop_label.configure(bg="#dcdcdc")

    # ===============================================
    # FUNCIONES Y LÓGICA
    # ===============================================
    # -----------------------------------------------
    # 1) Visualización de la imagen binaria
    # -----------------------------------------------
    #-----------------------------
    # Validar la imagen binaria
    #-----------------------------
    def validar_imagen(self):
        """
        Verifica que exista una imagen cargada.

        Retorna:
        bool: True si la imagen existe, False si no.
        """
        if self.img_binaria is None:
            messagebox.showwarning("Imagen requerida", "Primero carga una imagen.")
            print("Primero carga una imagen")
            return False
        return True

    # ----------------------------
    # Cargar la imagen binaria
    # ----------------------------
    def procesar_ruta(self, ruta):
        """
        Carga una imagen desde disco y la convierte a binaria.

        Proceso:
        1. Convertir a escala de grises
        2. Aplicar umbral (threshold)
        3. Guardar imagen original y binaria
        4. Mostrar en interfaz

        Parámetros:
        ruta (str): ruta del archivo
        """                                                              
        try:
            img_pil = Image.open(ruta).convert("L") # Escala de grises
            img = np.array(img_pil)
            
            # Umbral binario
            _, img_bin = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

            self.img = img
            self.img_binaria = img_bin

            # Convertir a PIL para mostrar
            img_pil_bin = Image.fromarray(img_bin)

            # Redimensionar manteniendo proporción
            max_size = (400, 400)
            img_pil_bin.thumbnail(max_size, Image.Resampling.LANCZOS)

            self.img_tk = ImageTk.PhotoImage(img_pil_bin)

            # Asegurar área fija
            self.label_img.config(image=self.img_tk, width=400, height=400, bg="black")
            self.label_img.image = self.img_tk

        except Exception as e:
            print("Error:", e)

    def cargar_imagen(self):
        """Abre explorador de archivos para seleccionar imagen."""
        ruta = filedialog.askopenfilename()
        if ruta:
            self.procesar_ruta(ruta)

    def drop_imagen(self, event):
        """Permite cargar imagen arrastrándola a la interfaz."""
        ruta = event.data
        if ruta.startswith("{") and ruta.endswith("}"):
            ruta = ruta[1:-1]
        self.procesar_ruta(ruta)

    # -----------------------------------------------
    # 2) Códigos de Cadena
    # -----------------------------------------------
    # Mostrar cadena
    def seleccionar_cadena(self):
        """
        Permite al usuario seleccionar una de las cadenas generadas.

        Retorna:
        list: cadena seleccionada o None si no hay
        """
        ventana = tk.Toplevel(self.root)
        ventana.title("Seleccionar cadena")

        tk.Label(ventana, text="Selecciona la cadena a analizar:").pack(pady=10)

        opciones = []

        # Detecta qué cadenas existen en memoria
        if hasattr(self, 'cadena_f4'):
            opciones.append("F4")
        if hasattr(self, 'cadena_f8'):
            opciones.append("F8")
        if hasattr(self, 'cadena_af8'):
            opciones.append("AF8")
        if hasattr(self, 'cadena_vcc'):
            opciones.append("VCC")
        if hasattr(self, 'cadena_3ot'):
            opciones.append("3OT")

        if not opciones:
            messagebox.showwarning("Advertencia", "No hay cadenas generadas.")
            ventana.destroy()
            return None

        seleccion = tk.StringVar(value=opciones[0])

        combo = ttk.Combobox(ventana, values=opciones, textvariable=seleccion, state="readonly")
        combo.pack(pady=10)

        resultado = {"cadena": None}

        def confirmar():
            tipo = seleccion.get()

            if tipo == "F4":
                resultado["cadena"] = self.cadena_f4
            elif tipo == "F8":
                resultado["cadena"] = self.cadena_f8
            elif tipo == "AF8":
                resultado["cadena"] = self.cadena_af8
            elif tipo == "VCC":
                resultado["cadena"] = self.cadena_vcc
            elif tipo == "3OT":
                resultado["cadena"] = self.cadena_3ot

            ventana.destroy()

        tk.Button(ventana, text="Aceptar", command=confirmar).pack(pady=10)

        ventana.grab_set()
        ventana.wait_window()

        return resultado["cadena"]

    # Contorno
    def detectar_contorno(self):
        """
        Detecta el contorno del objeto usando OpenCV.

        - Se obtiene el contorno externo
        - Se reordena para consistencia (top-left, sentido horario)
        - Se dibuja sobre la imagen
        """
        if not self.validar_imagen():
            return

        # Usamos la misma lógica que F8
        binary = self.img_binaria.copy()

        # Encontrar contornos
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        if not contours:
            messagebox.showerror("Error", "No se encontraron contornos.")
            print("No se encontraron contornos")
            return

        # Tomar el contorno más grande
        cnt = max(contours, key=cv2.contourArea)

        # Reordenar para que empiece en top-left y sea horario
        cnt = self.rotate_contour_to_start(cnt)

        # Convertir imagen a color para dibujar
        img_color = cv2.cvtColor(self.img_binaria, cv2.COLOR_GRAY2BGR)

        # Dibujar contorno en rojo
        for i in range(len(cnt)):
            x, y = cnt[i][0]
            img_color[y, x] = [255, 0, 0]  # rojo (BGR)

        # Punto inicial
        x0, y0 = cnt[0][0]

        # Dibujar punto inicial grande y visible
        cv2.circle(img_color, (x0, y0), 4, (0, 255, 0), -1)  # verde

        # Mostrar imagen
        img_pil = Image.fromarray(img_color)
        self.img_tk = ImageTk.PhotoImage(img_pil)

        self.label_img.config(image=self.img_tk)
        self.label_img.image = self.img_tk

        print(f"Contorno detectado con {len(cnt)} puntos")
        print(f"Punto inicial: ({x0}, {y0})")

    # ----- Códigos de cadena -----
    # Función auxiliar para encontrar el punto inicial
    def find_start_point(self, binary):
        """
        Encuentra un punto inicial válido del contorno.

        Estrategia:
        - Se busca un píxel blanco (255)
        - Que tenga fondo arriba o a la izquierda
        → asegura que estamos en el borde

        Parámetros:
        binary (ndarray): imagen binaria

        Retorna:
        (x, y) o None
        """
        padded = np.pad(binary, 1, 'constant', constant_values=0)

        for y in range(1, padded.shape[0] - 1):
            for x in range(1, padded.shape[1] - 1):
                if padded[y, x] == 255:
                    if padded[y - 1, x] == 0 or padded[y, x - 1] == 0:
                        return x, y
        return None

    def trace_boundary(self, binary):
        """
        Implementación del algoritmo de seguimiento de contorno (F4).

        Idea:
        - Se recorre el borde siguiendo vecinos 4-conectados
        - Se usa regla de "giro a la izquierda"
        - Se genera la cadena de Freeman

        Codificación:
            0 → derecha
            1 → abajo
            2 → izquierda
            3 → arriba

        Parámetros:
        binary (ndarray): imagen binaria

        Retorna:
        list: cadena F4
        """
        directions_4 = {
            (1, 0): 0,
            (0, 1): 1,
            (-1, 0): 2,
            (0, -1): 3
        }
        inv_dir_4 = {v: k for k, v in directions_4.items()}

        padded = np.pad(binary, 1, 'constant', constant_values=0)

        start_point = self.find_start_point(binary)
        if start_point is None:
            return []

        start_x, start_y = start_point

        vx, vy = start_x, start_y
        d = 0

        chain = []
        # Límite de seguridad para evitar loops infinitos
        for _ in range(10000):
            dx, dy = inv_dir_4[d]
            vx += dx
            vy += dy

            chain.append(d)
            # Condición de cierre
            if (vx, vy) == (start_x, start_y) and len(chain) > 0:
                break
            # Regla: girar izquierda
            d = (d + 3) % 4
            # Buscar siguiente vecino válido
            for _ in range(4):
                dx, dy = inv_dir_4[d]

                if d == 0:
                    px, py = vx, vy
                elif d == 1:
                    px, py = vx - 1, vy
                elif d == 2:
                    px, py = vx - 1, vy - 1
                else:
                    px, py = vx, vy - 1

                if padded[py, px] == 255:
                    break

                d = (d + 1) % 4

        return chain

    # ----------------------------
    # Función auxiliar para rotar (códigos de cadena)
    # ----------------------------
    def rotate_contour_to_start(self, contour):
        """
        Reordena el contorno para iniciar en el punto más arriba-izquierda.

        También invierte el orden para hacerlo horario.

        Esto es importante porque:
        - Hace consistente la cadena generada
        - Evita ambigüedad en análisis posteriores

        Parámetros:
        contour (ndarray)

        Retorna:
        ndarray
        """
        if contour.size == 0:
            return contour

        points = contour.reshape(-1, 2)

        # Top-left: menor y, luego menor x
        start_idx = min(range(len(points)), key=lambda i: (points[i][1], points[i][0]))

        rotated = np.concatenate((points[start_idx:], points[:start_idx]), axis=0)

        # Hacerlo horario
        rotated = rotated[::-1]

        return rotated.reshape((-1, 1, 2)).astype(contour.dtype)

    # ----------------------------
    # 2.1) F4
    # ----------------------------
    #  3
    # 2 0
    #  1
    def generar_f4(self):
        """
        Genera la cadena de Freeman 4 (F4) del contorno.

        Resultado:
        - Guarda en self.cadena_f4
        - Muestra cadena y longitud en interfaz
        """
        if not self.validar_imagen():
            return

        cadena_f4 = self.trace_boundary(self.img_binaria)

        if not cadena_f4:
            messagebox.showerror("Error", "No se pudo generar la cadena F4.")
            print("No se pudo generar F4")
            return

        cadena_str = ''.join(map(str, cadena_f4))

        # Guardar cadena F4
        self.cadena_f4 = cadena_f4

        self.text_resultado.delete("1.0", tk.END)
        self.text_resultado.insert(tk.END, f"Cadena F4:\n{cadena_str}\n")
        self.text_resultado.insert(tk.END, f"\nLongitud: {len(cadena_f4)}")

    # ----------------------------
    # 2.2) F8
    # ----------------------------
    # 5 6 7
    # 4   0
    # 3 2 1
    def generar_f8(self):
        """
        Genera el código de cadena Freeman 8.
        Usa diferencias entre puntos consecutivos.
        """
        if not self.validar_imagen():
            return

        # IMPORTANTE: invertir (igual que tu código de referencia)
        binary = self.img_binaria.copy()

        # Encontrar contornos
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        if not contours:
            messagebox.showerror("Error", "No se encontraron contornos.")
            print("No se encontraron contornos.")
            return

        # Contorno más grande
        cnt = max(contours, key=cv2.contourArea)

        # Reordenar
        cnt = self.rotate_contour_to_start(cnt)

        # Direcciones F8 (igual que tu referencia)
        directions_8 = {
            (0, 1): 0,
            (1, 1): 1,
            (1, 0): 2,
            (1, -1): 3,
            (0, -1): 4,
            (-1, -1): 5,
            (-1, 0): 6,
            (-1, 1): 7
        }

        chain_code_8 = []

        for i in range(len(cnt)):
            curr = cnt[i][0]
            nxt = cnt[(i + 1) % len(cnt)][0]

            dy = nxt[1] - curr[1]
            dx = nxt[0] - curr[0]

            if (dy, dx) in directions_8:
                chain_code_8.append(directions_8[(dy, dx)])

        # Ajuste final (IMPORTANTE)
        if chain_code_8:
            chain_code_8 = chain_code_8[-1:] + chain_code_8[:-1]

        cadena_str = ''.join(map(str, chain_code_8))

        # Guardar para futuro uso
        self.cadena_f8 = chain_code_8

        self.text_resultado.delete("1.0", tk.END)
        self.text_resultado.insert(tk.END, f"Cadena F8:\n{cadena_str}\n")
        self.text_resultado.insert(tk.END, f"\nLongitud: {len(chain_code_8)}")

    # ----------------------------
    # 2.3) AF8
    # ----------------------------
    def generar_af8(self):
        """
        Genera código AF8 (diferencial de F8).
        Representa cambios relativos en dirección.
        """
        if not hasattr(self, 'cadena_f8'):
            messagebox.showwarning("Advertencia", "Primero genera F8.")
            print("Primero genera F8")
            return

        f8 = self.cadena_f8

        if len(f8) < 2:
            messagebox.showwarning("Advertencia", "Cadena F8 demasiado corta")
            print("Cadena F8 demasiado corta")
            return

        # Tabla (si no la pusiste en __init__)
        F8toAF8 = {
            (0, 0): 0, (0, 1): 1, (0, 2): 2, (0, 3): 3, (0, 4): 4, (0, 5): 5, (0, 6): 6, (0, 7): 7,
            (1, 0): 7, (1, 1): 0, (1, 2): 1, (1, 3): 2, (1, 4): 3, (1, 5): 4, (1, 6): 5, (1, 7): 6,
            (2, 0): 6, (2, 1): 7, (2, 2): 0, (2, 3): 1, (2, 4): 2, (2, 5): 3, (2, 6): 4, (2, 7): 5,
            (3, 0): 5, (3, 1): 6, (3, 2): 7, (3, 3): 0, (3, 4): 1, (3, 5): 2, (3, 6): 3, (3, 7): 4,
            (4, 0): 4, (4, 1): 5, (4, 2): 6, (4, 3): 7, (4, 4): 0, (4, 5): 1, (4, 6): 2, (4, 7): 3,
            (5, 0): 3, (5, 1): 4, (5, 2): 5, (5, 3): 6, (5, 4): 7, (5, 5): 0, (5, 6): 1, (5, 7): 2,
            (6, 0): 2, (6, 1): 3, (6, 2): 4, (6, 3): 5, (6, 4): 6, (6, 5): 7, (6, 6): 0, (6, 7): 1,
            (7, 0): 1, (7, 1): 2, (7, 2): 3, (7, 3): 4, (7, 4): 5, (7, 5): 6, (7, 6): 7, (7, 7): 0
        }

        af8 = []

        # Conversión
        for i in range(len(f8)):
            prev = f8[i - 1]  # circular
            curr = f8[i]

            af8.append(F8toAF8[(prev, curr)])

        cadena_str = ''.join(map(str, af8))
        self.cadena_af8 = af8

        self.text_resultado.delete("1.0", tk.END)
        self.text_resultado.insert(tk.END, f"Cadena AF8:\n{cadena_str}\n")
        self.text_resultado.insert(tk.END, f"\nLongitud: {len(af8)}")

    # ----------------------------
    # 2.4) VCC
    # ----------------------------
    def generar_vcc(self):
        """
        Genera Vertex Chain Code a partir de F4.
        """
        if not hasattr(self, 'cadena_f4'):
            messagebox.showwarning("Advertencia", "Primero genera F4.")
            print("Primero genera F4")
            return

        f4 = self.cadena_f4

        if len(f4) < 2:
            messagebox.showwarning("Advertencia", "Cadena F4 demasiado corta")
            print("Cadena F4 demasiado corta")
            return

        F4toVCC = {
            (0, 0): 0,
            (0, 1): 1,
            (0, 3): 2,
            (1, 0): 2,
            (1, 1): 0,
            (1, 2): 1,
            (2, 1): 2,
            (2, 2): 0,
            (2, 3): 1,
            (3, 0): 1,
            (3, 2): 2,
            (3, 3): 0
        }

        vcc = []

        # Conversión circular
        for i in range(len(f4)):
            prev = f4[i - 1]
            curr = f4[i]

            if (prev, curr) in F4toVCC:
                vcc.append(F4toVCC[(prev, curr)])
            else:
                # Por seguridad (no debería pasar)
                vcc.append(0)

        cadena_str = ''.join(map(str, vcc))
        self.cadena_vcc = vcc

        self.text_resultado.delete("1.0", tk.END)
        self.text_resultado.insert(tk.END, f"Cadena VCC:\n{cadena_str}\n")
        self.text_resultado.insert(tk.END, f"\nLongitud: {len(vcc)}")

    # ----------------------------
    # 2.5) 3OT
    # ----------------------------
    def generar_3ot(self):
        """
        Genera código 3OT basado en cambios estructurales del contorno.
        """
        if not hasattr(self, 'cadena_f4'):
            messagebox.showwarning("Advertencia", "Primero genera F4.")
            print("Primero genera F4")
            return

        f4 = self.cadena_f4
        n = len(f4)

        if n < 2:
            messagebox.showwarning("Advertencia", "Cadena F4 demasiado corta")
            print("Cadena 3OT demasiado corta")
            return

        c3ot = []

        ref = f4[0]
        support = f4[0]
        primer_cambio_detectado = False

        # Recorrido principal
        for i in range(1, n):
            change = f4[i]

            if change == support:
                c3ot.append(0)
            else:
                if not primer_cambio_detectado:
                    c3ot.append(2)
                    primer_cambio_detectado = True
                elif change == ref:
                    c3ot.append(1)
                    ref = support
                elif (change - ref) % 4 == 2:
                    c3ot.append(2)
                    ref = support
                else:
                    c3ot.append(1)
                    ref = support

            support = change

        # Cierre circular
        change = f4[0]

        if change == support:
            c3ot.append(0)
        elif not primer_cambio_detectado:
            c3ot.append(2)
        elif change == ref:
            c3ot.append(1)
        elif (change - ref) % 4 == 2:
            c3ot.append(2)
        else:
            c3ot.append(1)

        cadena_str = ''.join(map(str, c3ot))
        self.cadena_3ot = c3ot

        self.text_resultado.delete("1.0", tk.END)
        self.text_resultado.insert(tk.END, f"Cadena 3OT:\n{cadena_str}\n")
        self.text_resultado.insert(tk.END, f"\nLongitud: {len(c3ot)}")


        # ------------------------------
    # Función auxiliar para obtener la cadena
    # ------------------------------
    def obtener_cadena_desde_texto(self):
        texto = self.text_resultado.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showwarning("Advertencia", "Primero ingresa una cadena.")
            return None
        return [int(c) for c in texto if c.isdigit()]

    # ------------------------------
    # Función auxiliar para expandir la imagen
    # ------------------------------
    def expandir_imagen(self, img, x, y):
        h, w = img.shape
        new_h, new_w = h, w
        offset_x, offset_y = 0, 0

        if x < 0:
            offset_x = 10
            new_h += 10
        elif x >= h:
            new_h += 10

        if y < 0:
            offset_y = 10
            new_w += 10
        elif y >= w:
            new_w += 10

        new_img = np.zeros((new_h, new_w), dtype=np.uint8)
        new_img[offset_x:offset_x+h, offset_y:offset_y+w] = img

        x += offset_x
        y += offset_y

        return new_img, x, y
    
    # ------------------------------
    # Función auxiliar para obtener el contorno
    # ------------------------------
    def obtener_contorno(self):
        if not self.validar_imagen():
            return None

        binary = self.img_binaria.copy()

        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        if not contours:
            return None

        cnt = max(contours, key=cv2.contourArea)
        cnt = self.rotate_contour_to_start(cnt)

        return cnt
    
    # ------------------------------
    # Función auxiliar para rellenar la imagen
    # ------------------------------
    def rellenar_la_imagen(self):
        cnt = self.obtener_contorno()
        if cnt is None:
            return None

        img_rellena = np.zeros_like(self.img_binaria)
        cv2.drawContours(img_rellena, [cnt], -1, 255, thickness=-1)

        return img_rellena

    # ------------------------------
    # 3) DECODIFICACION 
    # ------------------------------
    # DECODIFICAR F4 
    def decodificar_f4(self):

        # Obtener cadena desde el textbox
        cadena = self.obtener_cadena_desde_texto()
        if cadena is None:
            return

        # Reconstruir contorno desde la cadena F4
        img = self.mostrar_f4_imagen(cadena)

        # Guardar como imagen actual
        self.img_binaria = img
        #self.img = img

        # Rellenar el interior del contorno
        img = self.rellenar_la_imagen()

        # Si el relleno fue exitoso
        if img is not None:

            # Actualizar imagen con relleno
            self.img_binaria = img
            self.img = img

            # Mostrar resultado
            self.mostrar_imagen_resultado(img)

        # Mostrar imagen final
        self.mostrar_imagen_resultado(img)

    def mostrar_f4_imagen(self, cadena, size=(100, 100)):
        # Crear imagen vacía
        img = np.zeros(size, dtype=np.uint8)

        # Punto inicial en el centro
        x, y = size[0]//2, size[1]//2

        # Direcciones del código F4
        moves = {0:(0,1), 1:(1,0), 2:(0,-1), 3:(-1,0)}

        # Recorrer la cadena
        for d in cadena:

            # Obtener desplazamiento
            dx, dy = moves[d]

            # Actualizar posición
            x += dx
            y += dy

            # Expandir imagen si se sale de los límites
            if not (0 <= x < img.shape[0] and 0 <= y < img.shape[1]):
                img, x, y = self.expandir_imagen(img, x, y)

            # Dibujar pixel del contorno
            img[x, y] = 255

        # Regresar imagen generada
        return img

    # DECODIFICAR F8 
    def decodificar_f8(self):
        # Obtener cadena desde el textbox
        cadena = self.obtener_cadena_desde_texto()
        if cadena is None:
            return

        # Reconstruir contorno desde F8
        img = self.decodificar_f8_imagen(cadena)

        # Guardar como imagen actual
        self.img_binaria = img
        #self.img = img

        # Rellenar interior del contorno
        img = self.rellenar_la_imagen()

        # Si el relleno fue exitoso
        if img is not None:

            # Actualizar imagen con relleno
            self.img_binaria = img
            self.img = img

            # Mostrar resultado
            self.mostrar_imagen_resultado(img)

        # Mostrar imagen final
        self.mostrar_imagen_resultado(img)

    def decodificar_f8_imagen(self, cadena, size=(100, 100)):
        # Crear imagen vacía
        img = np.zeros(size, dtype=np.uint8)

        # Punto inicial en el centro
        x, y = size[0]//2, size[1]//2

        # Direcciones del código F8 (8 vecinos)
        moves = {0:(0,1), 1:(1,1), 2:(1,0), 3:(1,-1),
                4:(0,-1), 5:(-1,-1), 6:(-1,0), 7:(-1,1)}

        # Recorrer la cadena
        for d in cadena:

            # Obtener desplazamiento
            dx, dy = moves[d]

            # Actualizar posición
            x += dx
            y += dy

            # Expandir imagen si se sale de los límites
            if not (0 <= x < img.shape[0] and 0 <= y < img.shape[1]):
                img, x, y = self.expandir_imagen(img, x, y)

            # Dibujar pixel del contorno
            img[x, y] = 255

        # Regresar imagen generada
        return img


    # DECODIFICAR AF8
    # AF8 a F8 
    def af8_a_f8(self, af8):
        """
        Convierte AF8 a F8 probando todas las direcciones iniciales.
        Selecciona la que genera un contorno cerrado.
        """

        # Movimientos F8
        moves = {
            0:(0,1), 1:(1,1), 2:(1,0), 3:(1,-1),
            4:(0,-1), 5:(-1,-1), 6:(-1,0), 7:(-1,1)
        }

        # Probar todas las posibles direcciones iniciales
        for inicial in range(8):

            f8 = []
            estado_actual = inicial

            # Reconstrucción
            for simbolo_relativo in af8:
                estado_actual = (estado_actual + simbolo_relativo) % 8
                f8.append(estado_actual)

            # Validar cierre geométrico
            x, y = 0, 0
            for d in f8:
                dx, dy = moves[d]
                x += dx
                y += dy

            if x == 0 and y == 0:
                return f8  # encontró una solución válida

        # Si ninguna cierra, devolver la última 
        print("Advertencia: AF8 no genera contorno cerrado con ningún inicial.")
        return f8

    # DECODIFICAR AF8 A IMAGEN
    def decodificar_af8(self):
        cadena = self.obtener_cadena_desde_texto()
        if not cadena:
            return
        
        # 1. AF8 a F8
        f8 = self.af8_a_f8(cadena)
        
        # 2. Dibujar contorno
        img = self.decodificar_f8_imagen(f8)

        # 3. Guardar como imagen actual
        self.img_binaria = img

        # 4. Rellenar
        img = self.rellenar_la_imagen()

        if img is not None:
            self.img_binaria = img
            self.img = img

        img = np.rot90(img)

        # 5. Mostrar
        self.mostrar_imagen_resultado(img)

    # VCC a F4 
    def vcc_a_f4(self, vcc, inicial=0):
        """
        Convierte VCC a Freeman 4.
        vcc: lista de símbolos [1, 2, 3]
        inicial: dirección de entrada al primer vértice (default 0)
        """
        # Matriz de transición basada en  (dirección_anterior, símbolo_vcc) -> dirección_nueva
        tabla_vcc = {
            # Si venía de 0 (Derecha)
            (0, 1): 1, (0, 2): 3, (0, 3): 0,
            # Si venía de 1 (Arriba)
            (1, 1): 2, (1, 2): 0, (1, 3): 1,
            # Si venía de 2 (Izquierda)
            (2, 1): 3, (2, 2): 1, (2, 3): 2,
            # Si venía de 3 (Abajo)
            (3, 1): 0, (3, 2): 2, (3, 3): 3
        }
        
        f4 = []
        prev = inicial
        
        for simbolo in vcc:
            if (prev, simbolo) in tabla_vcc:
                nuevo_f4 = tabla_vcc[(prev, simbolo)]
                f4.append(nuevo_f4)
                prev = nuevo_f4
            else:
                # En caso de símbolo inválido, mantiene dirección    
                f4.append(prev)
                
        return f4

    # DECODIFICAR VCC
    def decodificar_vcc(self):
        cadena = self.obtener_cadena_desde_texto()
        if not cadena:
            return
        
        # 1. VCC a F4
        f4 = self.vcc_a_f4(cadena)
        
        # 2. Dibujar contorno
        img = self.mostrar_f4_imagen(f4)

        # 3. Guardar
        self.img_binaria = img

        # 4. Rellenar
        img = self.rellenar_la_imagen()

        if img is not None:
            self.img_binaria = img
            self.img = img

        img = np.rot90(img)

        # 5. Mostrar
        self.mostrar_imagen_resultado(img)


    # 3OT a F4 
    def c3ot_a_f4(self, c3ot):
            
            mejor_f4 = None
            mejor_distancia = float('inf')
            
            moves = {0: (1, 0), 1: (0, 1), 2: (-1, 0), 3: (0, -1)}

            # Probamos las 4 direcciones iniciales
            for inicial in range(4):
                # Como el primer cambio en código siempre es '2', no sabemos si fue +1 o -1.
                # Probamos ambas posibilidades para el primer giro (giro=1 y giro=-1).
                for sentido_primer_giro in [1, -1]:
                    f4 = []
                    dir_actual = inicial
                    ref = inicial
                    support = inicial
                    primer_cambio_visto = False
                    
                    x, y = 0, 0
                    posible = True

                    for simbolo in c3ot:
                        if simbolo == 0:
                            # Se mantiene la dirección del support
                            nueva_dir = support
                        else:
                            # Es un giro (1 o 2)
                            if not primer_cambio_visto:
                                # Aplicamos el sentido que estamos probando en este bucle
                                nueva_dir = (support + sentido_primer_giro) % 4
                                primer_cambio_visto = True
                            else:
                                # Buscamos qué dirección (D o I) generaría este símbolo
                                encontrada = False
                                for giro in [1, -1]:
                                    prueba_dir = (support + giro) % 4
                                    
                                    s_generado = None
                                    if prueba_dir == ref:
                                        s_generado = 1
                                    elif (prueba_dir - ref) % 4 == 2:
                                        s_generado = 2
                                    else:
                                        s_generado = 1
                                    
                                    if s_generado == simbolo:
                                        nueva_dir = prueba_dir
                                        encontrada = True
                                        break
                                
                                if not encontrada:
                                    posible = False
                                    break
                            
                            # Actualizamos ref
                            ref = support
                        
                        # Actualizamos support y trayectoria
                        support = nueva_dir
                        f4.append(nueva_dir)
                        dx, dy = moves[nueva_dir]
                        x += dx
                        y += dy

                    if posible:
                        distancia = abs(x) + abs(y)
                        if distancia < mejor_distancia:
                            mejor_distancia = distancia
                            mejor_f4 = f4
                            if distancia == 0: break 

            return mejor_f4, (mejor_distancia == 0)

    # DECODIFICAR 3OT
    def decodificar_3ot(self):
        cadena = self.obtener_cadena_desde_texto()
        if not cadena:
            return
        
        f4, cierra = self.c3ot_a_f4(cadena)
        
        img = self.mostrar_f4_imagen(f4)

        self.img_binaria = img

        if not cierra:
            messagebox.showwarning(
                "Advertencia",
                "La cadena 3OT no cierra correctamente. Se mostrará solo el contorno."
            )

            self.text_resultado.insert(tk.END, "\nEstado: No cerrada\n")

            self.mostrar_imagen_resultado(img)
            return

        img_rellena = self.rellenar_la_imagen()

        if img_rellena is not None:
            self.img_binaria = img_rellena
            self.img = img_rellena
            img = img_rellena

        self.mostrar_imagen_resultado(img)

    # ------------------------------
    # Mostrar Imagen
    # ------------------------------
    def mostrar_imagen_resultado(self, img):
        img_pil = Image.fromarray(img)

        # Redimensionar manteniendo proporción
        max_size = (400, 400)
        img_pil.thumbnail(max_size, Image.Resampling.LANCZOS)

        self.img_tk = ImageTk.PhotoImage(img_pil)

        # Mantener tamaño fijo visual
        self.label_img.config(image=self.img_tk, width=400, height=400, bg="black")
        self.label_img.image = self.img_tk

    def cierra_figura_f4(self, f4):
        x, y = 0, 0
        moves = {0:(0,1), 1:(1,0), 2:(0,-1), 3:(-1,0)}

        for d in f4:
            dx, dy = moves[d]
            x += dx
            y += dy

        return x == 0 and y == 0

    # -----------------------------
    # 4) Histograma
    # -----------------------------
    def mostrar_histograma(self):
        """
        Muestra histograma de frecuencias y probabilidades.
        """
        cadena = self.seleccionar_cadena()
        if cadena is None or len(cadena) == 0:
            messagebox.showwarning("Advertencia", "Cadena vacía")
            return

        conteo = Counter(cadena)
        total = len(cadena)

        simbolos = sorted(conteo.keys())
        frecuencias = [conteo[s] for s in simbolos]
        probabilidades = [f / total for f in frecuencias]

        # Crear ventana nueva
        ventana = tk.Toplevel(self.root)
        ventana.title("Histograma")

        # Gráfica
        fig, axf = plt.subplots(figsize=(6, 4))

        # Barras
        axf.bar(simbolos, frecuencias, width=0.9, color="orange")

        axf.set_xlabel("Símbolo")
        axf.set_ylabel("Frecuencia")

        axf.set_xlim(-0.5, max(simbolos) + 0.5)
        axf.set_xticks(np.arange(min(simbolos), max(simbolos)+1))

        axf.set_ylim(0, max(frecuencias) + max(1, max(frecuencias)//10))
        axf.set_yticks(np.arange(0, max(frecuencias)+1, max(1, max(frecuencias)//10)))

        # Probabilidad
        axp = axf.twinx()
        axp.plot(simbolos, probabilidades, marker='.', linewidth=2, color="red")

        axp.set_ylabel("Probabilidad")
        axp.set_ylim(0, max(probabilidades)*1.2)
        axp.set_yticks(np.arange(0, 1.1, 0.1))

        axf.set_title("Frecuencia y Probabilidad del Código de Cadena")

        canvas = FigureCanvasTkAgg(fig, master=ventana)
        canvas.draw()
        canvas.get_tk_widget().pack()

        # Tabla
        tabla_texto = tk.Text(ventana, height=10)
        tabla_texto.pack()

        tabla_texto.insert(tk.END, "Símbolo\tFrecuencia\tProbabilidad\n")
        for s, f, p in zip(simbolos, frecuencias, probabilidades):
            tabla_texto.insert(tk.END, f"{s}\t{f}\t{p:.4f}\n")

    # ---------------------------
    # 5) Entropía
    # ---------------------------
    def mostrar_entropia(self):
        """
        Calcula entropía de Shannon.
        """
        cadena = self.seleccionar_cadena()
        if cadena is None:
            return

        conteo = Counter(cadena)
        total = len(cadena)

        entropia = 0
        for f in conteo.values():
            p = f / total
            entropia -= p * np.log2(p)

        ventana = tk.Toplevel(self.root)
        ventana.title("Entropía")

        label = tk.Label(ventana, text=f"Entropía de Shannon:\n{entropia:.4f}", font=("Arial", 14))
        label.pack(pady=20)


    # -----------------------------
    # 6) Compresión de Huffman y
    # 7) Comprensión de Aritmética
    # -----------------------------
    def comprimir(self):
        """
        Aplica compresión Huffman y calcula eficiencia.
        """
        datos_cadena = self.seleccionar_cadena()
        if datos_cadena is None or len(datos_cadena) == 0:
            messagebox.showwarning("Advertencia", "Cadena vacía")
            return

        total_elementos = len(datos_cadena)
        conteo_simbolos = Counter(datos_cadena)

        # Entropía De Shannon
        entropia_shannon = 0.0
        for frecuencia in conteo_simbolos.values():
            probabilidad = frecuencia / total_elementos
            entropia_shannon -= probabilidad * np.log2(probabilidad)

        # Probabilidades
        diccionario_probabilidades = {
            simbolo: freq / total_elementos
            for simbolo, freq in conteo_simbolos.items()
        }

        # 7) Longitud Aritmética
        longitud_aritmetica = 0.0
        for simbolo in diccionario_probabilidades:
            prob = diccionario_probabilidades[simbolo]

            if prob > 0:
                log_base2 = np.log(prob) / np.log(2)
                longitud_aritmetica += prob * (-log_base2)

        # 6) Huffman
        cola_prioridad = [[freq, [simb, ""]] for simb, freq in conteo_simbolos.items()]
        heapq.heapify(cola_prioridad)

        while len(cola_prioridad) > 1:
            nodo_menor = heapq.heappop(cola_prioridad)
            nodo_mayor = heapq.heappop(cola_prioridad)

            for elemento in nodo_menor[1:]:
                elemento[1] = '0' + elemento[1]

            for elemento in nodo_mayor[1:]:
                elemento[1] = '1' + elemento[1]

            nodo_combinado = [nodo_menor[0] + nodo_mayor[0]] + nodo_menor[1:] + nodo_mayor[1:]
            heapq.heappush(cola_prioridad, nodo_combinado)

        codigos_huffman = heapq.heappop(cola_prioridad)[1:]

        # Longitud Promedio Huffman
        total_bits = 0
        for simbolo, codigo_binario in codigos_huffman:
            frecuencia = conteo_simbolos[simbolo]
            total_bits += frecuencia * len(codigo_binario)

        longitud_promedio = total_bits / total_elementos

        # Eficiencia
        eficiencia = entropia_shannon / longitud_promedio if longitud_promedio != 0 else 0

        # Ventana externa que despliega resultados
        ventana = tk.Toplevel(self.root)
        ventana.title("Resultado de la Compresión de Huffman y Compresión Aritmética")
        ventana.geometry("400x400")

        titulo = tk.Label(ventana, text="Resultados de Compresión", font=("Arial", 14, "bold"))
        titulo.pack(pady=10)

        frame = tk.Frame(ventana)
        frame.pack(pady=10)

        # ---- Códigos Huffman ----
        texto_codigos = ""
        for simbolo, codigo_binario in sorted(codigos_huffman):
            texto_codigos += f"{simbolo}: {codigo_binario}\n"

        lbl_codigos = tk.Label(frame, text=f"Códigos Huffman:\n{texto_codigos}", justify="left")
        lbl_codigos.pack(anchor="w")

        # ---- Métricas ----
        lbl_entropia = tk.Label(frame, text=f"Entropía: {entropia_shannon:.4f}")
        lbl_huffman = tk.Label(frame, text=f"Longitud Huffman: {longitud_promedio:.4f}")
        lbl_aritmetica = tk.Label(frame, text=f"Longitud aritmética: {longitud_aritmetica:.4f}")
        lbl_eficiencia = tk.Label(frame, text=f"Eficiencia: {eficiencia:.4f}")

        lbl_entropia.pack(anchor="w", pady=2)
        lbl_huffman.pack(anchor="w", pady=2)
        lbl_aritmetica.pack(anchor="w", pady=2)
        lbl_eficiencia.pack(anchor="w", pady=2)
    
    # -----------------------------------------------
    # 8) Propiedades Geométricas (Funciones y lógica)
    # -----------------------------------------------
    def mostrar_propiedades(self):
        """
        Calcula propiedades geométricas del objeto:

        - Perímetro (longitud F4)
        - Área (pixeles blancos)
        - Perímetro de contacto (vecindad 4)
        - Característica de Euler (C - H)
        - Compacidad discreta

        Requiere:
        - Imagen binaria
        - Cadena F4 generada
        """
        if self.img_binaria is None:
            messagebox.showwarning("Advertencia", "Primero carga una imagen")
            return

        if not hasattr(self, 'cadena_f4') or self.cadena_f4 is None:
            messagebox.showwarning("Advertencia", "Primero calcula la cadena F4")
            return

        # ------ Crear ventana nueva ------
        ventana = tk.Toplevel(self.root)
        ventana.title("Propiedades geométricas")
        ventana.geometry("400x300")

        # ------ Título ------
        titulo = tk.Label(ventana, text="Propiedades del objeto", font=("Arial", 14, "bold"))
        titulo.pack(pady=10)

        # ------ Frame para organizar mejor ------
        frame = tk.Frame(ventana)
        frame.pack(pady=10)

        # ------ Etiquetas (por ahora vacías o placeholders) ------
        self.lbl_perimetro = tk.Label(frame, text="Perímetro: ")
        self.lbl_area = tk.Label(frame, text="Área: ")
        self.lbl_per_contacto = tk.Label(frame, text="Perímetro de contacto: ")
        self.lbl_euler = tk.Label(frame, text="Característica de Euler: ")
        self.lbl_compacidad = tk.Label(frame, text="Compacidad discreta: ")

        # ------ Mostrar en columna ------
        self.lbl_perimetro.pack(anchor="w")
        self.lbl_area.pack(anchor="w")
        self.lbl_per_contacto.pack(anchor="w")
        self.lbl_euler.pack(anchor="w")
        self.lbl_compacidad.pack(anchor="w")

        # 8.1) Calcular perímetro
        perimetro = int(len(self.cadena_f4))

        # 8.2) Calcular área
        area = int(np.count_nonzero(self.img_binaria))

        # 8.3) Calcular perímetro de contacto
        perimetro_contacto = 0

        filas, columnas = self.img_binaria.shape

        for i in range(filas):
            for j in range(columnas):
                if self.img_binaria[i, j] == 255:

                    # Vecinos 4
                    vecinos = [
                        (i-1, j),  # arriba
                        (i+1, j),  # abajo
                        (i, j-1),  # izquierda
                        (i, j+1)   # derecha
                    ]

                    for ni, nj in vecinos:
                        # Si está fuera de la imagen también se cuenta como fondo
                        if (ni < 0 or ni >= filas or
                            nj < 0 or nj >= columnas or
                            self.img_binaria[ni, nj] == 0):
                            perimetro_contacto += 1
        
        # 8.4) Cálculo de la caract. de Euler ------
        
        # Binarizar imagen
        img_bin = self.img_binaria // 255
        # Obtener componentes conectados
        num_labels_obj, _ = cv2.connectedComponents(img_bin.astype(np.uint8))
        # Quita el fondo
        C = num_labels_obj - 1
        # Detectar huecos
        # Invertir la imagen
        img_inv = 1 - img_bin
        num_labels_fondo, labels_fondo = cv2.connectedComponents(img_inv.astype(np.uint8))
        # Quitar fondo externo (etiqueta del borde)
        # Etiquetas que tocan el borde
        bordes = np.unique(
            np.concatenate([
                labels_fondo[0, :],      # arriba
                labels_fondo[-1, :],     # abajo
                labels_fondo[:, 0],      # izquierda
                labels_fondo[:, -1]      # derecha
            ])
        )

        # Todas las etiquetas (excepto 0)
        todas = set(np.unique(labels_fondo))

        # Quitar fondo externo
        huecos_labels = todas - set(bordes)

        # Quitar fondo (label 0)
        if 0 in huecos_labels:
            huecos_labels.remove(0)

        H = len(huecos_labels)

        # Calcula Euler
        euler = C - H

        #print("Componentes:", C) # Prueba
        #print("Huecos:", H)

        # 8.5) Calcular compacidad discreta
        perimetro = len(self.cadena_f4)
        area = int(np.count_nonzero(self.img_binaria))

        compacidad = (perimetro ** 2) / area

        # Mostrar resultados
        self.lbl_perimetro.config(text=f"Perímetro: {perimetro}")
        self.lbl_area.config(text=f"Área: {area}")
        self.lbl_per_contacto.config(text=f"Perímetro de contacto: {perimetro_contacto}")
        self.lbl_euler.config(text=f"Característica de Euler: {euler}")
        self.lbl_compacidad.config(text=f"Compacidad discreta: {compacidad:.4f}") # Si nos da valores altos es más compacto, altos es irregular.


# ===============================================
# Main
# ===============================================
root = TkinterDnD.Tk()
app = App(root)
root.mainloop()