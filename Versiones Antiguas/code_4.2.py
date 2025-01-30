# Changes and improvements applied to the original code:

```python
import sys
import json
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Removed import csv since CSV functionality is not used in this version

sys.executable

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
        # Improved to handle division by zero
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
        # Changed to full screen based on screen dimensions
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.productos = []
        self.ventas = []
        self.proveedores = []
        self.product_frames = {}
        self.auto_repeat_delay = 100
        self.auto_repeat_id = None
        
        self.cargar_datos()
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        # Direct method calls for creating tabs instead of using a separate method
        self.crear_pestana_ventas()
        self.crear_pestana_stock()
        self.crear_pestana_analisis()
        self.crear_pestana_historial()
        self.crear_pestana_proveedores()

    # New methods for UI setup:
    
    def crear_pestana_ventas(self):
        self.tab_ventas = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_ventas, text='Realizar Ventas')
        
        # ... (implementation details for creating sales tab)

    def crear_pestana_proveedores(self):
        self.tab_proveedores = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_proveedores, text='Proveedores')
        
        # ... (implementation details for creating suppliers tab)

    def registrar_proveedor(self):
        # Method to register new suppliers
        datos = [entry.get() for entry in self.entries_proveedores]
        if not all(datos):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        nuevo_proveedor = Proveedor(*datos)
        self.proveedores.append(nuevo_proveedor)
        self.guardar_datos()
        self.actualizar_lista_proveedores()
        
        for entry in self.entries_proveedores:
            entry.delete(0, 'end')
        
        messagebox.showinfo("Éxito", "Proveedor registrado correctamente")

    def actualizar_lista_proveedores(self):
        # Method to update the supplier list in the UI
        for widget in self.scroll_proveedores.winfo_children():
            widget.destroy()

        for proveedor in self.proveedores:
            frame = ctk.CTkFrame(self.scroll_proveedores, corner_radius=5, fg_color="#404040")
            frame.pack(fill="x", pady=2, padx=5)

            ctk.CTkLabel(frame, text=proveedor.nombre, width=150, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(frame, text=proveedor.telefono, width=100).pack(side="left", padx=5)
            ctk.CTkLabel(frame, text=proveedor.direccion, width=200).pack(side="left", padx=5)

    # ... (rest of the methods would follow with similar commentary for changes or improvements)

    def cargar_datos(self):
        try:
            with open(ARCHIVO_PRODUCTOS, 'r') as f:
                self.productos = [Producto(**p) for p in json.load(f)]
            with open(ARCHIVO_VENTAS, 'r') as f:
                self.ventas = json.load(f)
            with open(ARCHIVO_PROVEEDORES, 'r') as f:
                self.proveedores = [Proveedor(**p) for p in json.load(f)]
        except FileNotFoundError:
            self.productos = []
            self.ventas = []
            self.proveedores = []
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file: {e}")
            self.productos = []
            self.ventas = []
            self.proveedores = []

    # ... (other methods like guardar_datos, actualizar_historial, etc., with inline comments as needed)

if __name__ == "__main__":
    root = ctk.CTk()
    app = GestionStock(root)
    root.mainloop()
