import sys
import json
import csv
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Archivos de datos
ARCHIVO_PRODUCTOS = "productos.json"
ARCHIVO_VENTAS = "ventas.json"
ARCHIVO_PROVEEDORES = "proveedores.json"
ARCHIVO_HISTORIAL = "historial_stock.json"  # Se agregó un nuevo archivo para almacenar el historial de movimientos de stock. Esto mejora el seguimiento de cambios en el inventario.
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
        return ((self.precio - self.costo) / self.precio) * 100 if self.precio > 0 else 0

class Proveedor:
    def __init__(self, nombre, telefono, direccion):
        self.nombre = nombre
        self.telefono = telefono
        self.direccion = direccion

class GestionStock:
    """
    Clase encargada de la gestión de stock en la ferretería.
    Se reorganizó la inicialización de la clase para mejorar la modularidad y facilitar la gestión de datos.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Stock - Ferretería")
        self.root.geometry("1024x768")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.productos, self.ventas, self.proveedores, self.historial = self.cargar_datos()
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)
        self.crear_pestanas()
    
    def registrar_movimiento_stock(self, producto, cantidad, tipo):
        """
        Nueva función para registrar los movimientos de stock.
        Permite mantener un historial de entradas y salidas de productos, mejorando la trazabilidad.
        """
        self.historial.append({
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "producto": producto.nombre,
            "cantidad": cantidad,
            "tipo": tipo
        })
        self.guardar_datos()  # Se agregó esta función para registrar los movimientos de stock, permitiendo un mejor control de inventario.
    
    def crear_pestanas(self):
        self.pestanas = {
            "ventas": self.crear_pestana_ventas(),
            "stock": self.crear_pestana_stock(),
            "analisis": self.crear_pestana_analisis(),
            "historial": self.crear_pestana_historial(),
            "proveedores": self.crear_pestana_proveedores()
        }
    
    def exportar_ventas_csv(self):
        """
        Se agregó una función para exportar ventas a CSV.
        Esto facilita la gestión y análisis externo de los datos de ventas.
        La función genera un archivo "ventas.csv" con los datos de ventas actuales.
        """
        with open("ventas.csv", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Fecha", "Producto", "Cantidad", "Total"])
            for venta in self.ventas:
                writer.writerow([venta['fecha'], venta['producto'], venta['cantidad'], f"${venta['total']:.2f}"])
        messagebox.showinfo("Éxito", "Ventas exportadas correctamente a ventas.csv")
    
    def cargar_datos(self):
        """
        Se actualizó para incluir la carga del historial de stock,
        permitiendo la persistencia de los movimientos de inventario.
        """
        try:
            with open(ARCHIVO_PRODUCTOS, 'r') as f:
                productos = [Producto(**p) for p in json.load(f)]
            with open(ARCHIVO_VENTAS, 'r') as f:
                ventas = json.load(f)
            with open(ARCHIVO_PROVEEDORES, 'r') as f:
                proveedores = [Proveedor(**p) for p in json.load(f)]
            with open(ARCHIVO_HISTORIAL, 'r') as f:
                historial = json.load(f)
        except FileNotFoundError:
            productos, ventas, proveedores, historial = [], [], [], []
        return productos, ventas, proveedores, historial
    
if __name__ == "__main__":
    root = ctk.CTk()
    app = GestionStock(root)
    root.mainloop()

