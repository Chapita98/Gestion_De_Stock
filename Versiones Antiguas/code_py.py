import sys
import json
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Add logging for better debugging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
ARCHIVO_PRODUCTOS = "productos.json"
ARCHIVO_VENTAS = "ventas.json"
ARCHIVO_PROVEEDORES = "proveedores.json"
MARGEN_MINIMO = 20

class Producto:
    def __init__(self, codigo, nombre, categoria, costo, precio, stock, stock_minimo=5):
        self.codigo = codigo
        self.nombre = nombre
        self.categoria = categoria
        self.costo = float(costo)
        self.precio = float(precio)
        self.stock = int(stock)
        self.stock_minimo = int(stock_minimo)

    @property
    def margen_ganancia(self):
        # Handle division by zero
        if self.precio == 0:
            return 0
        return ((self.precio - self.costo) / self.precio) * 100

class Proveedor:
    def __init__(self, nombre, telefono, direccion):
        self.nombre = nombre
        self.telefono = telefono
        self.direccion = direccion

class GestionStock:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Stock - Ferretería")
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.productos = []
        self.ventas = []
        self.proveedores = []
        self.product_frames = {}
        self.auto_repeat_delay = 100
        self.auto_repeat_id = None
        
        # Load data on initialization rather than in separate method for better organization
        self.cargar_datos()
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        # Create tabs
        self.crear_pestana_ventas()
        self.crear_pestana_stock()
        self.crear_pestana_analisis()
        self.crear_pestana_historial()
        self.crear_pestana_proveedores()

    def crear_pestana_ventas(self):
        self.tab_ventas = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_ventas, text='Realizar Ventas')
        
        # ... (existing code for sales tab)

    def crear_pestana_proveedores(self):
        self.tab_proveedores = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_proveedores, text='Proveedores')
        
        # ... (existing code for suppliers tab)

    def registrar_proveedor(self):
        datos = [entry.get() for entry in self.entries_proveedores]
        if not all(datos):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        nuevo_proveedor = Proveedor(*datos)
        self.proveedores.append(nuevo_proveedor)
        self.guardar_datos()
        self.actualizar_lista_proveedores()
        self.limpiar_campos_proveedor()  # New method to clear fields
        
        messagebox.showinfo("Éxito", "Proveedor registrado correctamente")

    def limpiar_campos_proveedor(self):
        # New method to clear entry fields after registration
        for entry in self.entries_proveedores:
            entry.delete(0, 'end')

    def actualizar_lista_proveedores(self):
        for widget in self.scroll_proveedores.winfo_children():
            widget.destroy()

        for proveedor in self.proveedores:
            frame = ctk.CTkFrame(self.scroll_proveedores, corner_radius=5, fg_color="#404040")
            frame.pack(fill="x", pady=2, padx=5)

            ctk.CTkLabel(frame, text=proveedor.nombre, width=150, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(frame, text=proveedor.telefono, width=100).pack(side="left", padx=5)
            ctk.CTkLabel(frame, text=proveedor.direccion, width=200).pack(side="left", padx=5)

    # Improved error handling and logging in data loading
    def cargar_datos(self):
        try:
            with open(ARCHIVO_PRODUCTOS, 'r') as f:
                self.productos = [Producto(**p) for p in json.load(f)]
            with open(ARCHIVO_VENTAS, 'r') as f:
                self.ventas = json.load(f)
            with open(ARCHIVO_PROVEEDORES, 'r') as f:
                self.proveedores = [Proveedor(**p) for p in json.load(f)]
        except FileNotFoundError as e:
            logging.warning(f"File not found: {e}")
            self.productos, self.ventas, self.proveedores = [], [], []
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON: {e}")
            self.productos, self.ventas, self.proveedores = [], [], []

    def guardar_datos(self):
        try:
            with open(ARCHIVO_PRODUCTOS, 'w') as f:
                json.dump([vars(p) for p in self.productos], f)
            with open(ARCHIVO_VENTAS, 'w') as f:
                json.dump(self.ventas, f)
            with open(ARCHIVO_PROVEEDORES, 'w') as f:
                json.dump([vars(p) for p in self.proveedores], f)
        except IOError as e:
            logging.error(f"Error saving data: {e}")
            messagebox.showerror("Error", "No se pudo guardar la información.")

    # ... (other methods with similar comments on improvements)

if __name__ == "__main__":
    root = ctk.CTk()
    app = GestionStock(root)
    root.mainloop()
