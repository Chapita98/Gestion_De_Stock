# gestion_stock.py
import sys
import json
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, ttk
import logging
import hashlib

# Configuración inicial
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
ARCHIVO_PRODUCTOS = "productos.json"
ARCHIVO_VENTAS = "ventas.json"
ARCHIVO_PROVEEDORES = "proveedores.json"
ARCHIVO_USUARIOS = "usuarios.json"
ARCHIVO_HISTORIAL = "historial.json"
MARGEN_MINIMO = 20

# Paleta de colores
COLOR_PRIMARIO = "#2b2b2b"
COLOR_SECUNDARIO = "#404040"
COLOR_ALERTA = "#FFD700"

class Usuario:
    def __init__(self, usuario, contrasena, clave_recuperacion, rol="normal"):
        self.usuario = usuario
        self.contrasena = self._hash_contrasena(contrasena)
        self.clave_recuperacion = clave_recuperacion
        self.rol = rol

    @staticmethod
    def _hash_contrasena(contrasena):
        return hashlib.sha256(contrasena.encode()).hexdigest()

class GestionStock:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Stock")
        self.root.withdraw()
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.productos = []
        self.ventas = []
        self.proveedores = []
        self.usuarios = []
        self.historial = []
        self.current_user = None
        
        self.cargar_datos()
        self.mostrar_login()
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

    # -------------------------------
    # Funciones principales
    # -------------------------------
    def cargar_datos(self):
        try:
            with open(ARCHIVO_PRODUCTOS, "r") as file:
                self.productos = json.load(file)
        except FileNotFoundError:
            self.productos = []

        try:
            with open(ARCHIVO_VENTAS, "r") as file:
                self.ventas = json.load(file)
        except FileNotFoundError:
            self.ventas = []

        try:
            with open(ARCHIVO_PROVEEDORES, "r") as file:
                self.proveedores = json.load(file)
        except FileNotFoundError:
            self.proveedores = []

        try:
            with open(ARCHIVO_USUARIOS, "r") as file:
                usuarios_data = json.load(file)
                self.usuarios = [Usuario(**user) for user in usuarios_data]
        except FileNotFoundError:
            self.usuarios = []

        try:
            with open(ARCHIVO_HISTORIAL, "r") as file:
                self.historial = json.load(file)
        except FileNotFoundError:
            self.historial = []

    def guardar_datos(self):
        with open(ARCHIVO_PRODUCTOS, "w") as file:
            json.dump(self.productos, file, indent=4)

        with open(ARCHIVO_VENTAS, "w") as file:
            json.dump(self.ventas, file, indent=4)

        with open(ARCHIVO_PROVEEDORES, "w") as file:
            json.dump(self.proveedores, file, indent=4)

        with open(ARCHIVO_USUARIOS, "w") as file:
            usuarios_data = [{"usuario": u.usuario, 
                            "contrasena": u.contrasena, 
                            "clave_recuperacion": u.clave_recuperacion, 
                            "rol": u.rol} for u in self.usuarios]
            json.dump(usuarios_data, file, indent=4)

        with open(ARCHIVO_HISTORIAL, "w") as file:
            json.dump(self.historial, file, indent=4)

    # -------------------------------
    # Funciones de interfaz
    # -------------------------------
    def mostrar_login(self):
        self.login_window = ctk.CTkToplevel(self.root)
        self.login_window.title("Inicio de Sesión")
        self.login_window.geometry("400x400")
        self.login_window.grab_set()

        # Controles de entrada
        campos = [
            ("Usuario:", ctk.CTkEntry),
            ("Contraseña:", ctk.CTkEntry(show="*")),
            ("Rol:", ctk.CTkComboBox(values=["admin", "normal"], state="readonly"))
        ]

        self.entries = []
        for i, (label, widget) in enumerate(campos):
            ctk.CTkLabel(self.login_window, text=label).pack(pady=5)
            entry = widget(self.login_window)
            entry.pack(pady=5)
            self.entries.append(entry)
            if label == "Rol:":
                entry.set("normal")

        # Botones
        btn_frame = ctk.CTkFrame(self.login_window, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Iniciar Sesión", 
                    command=self.iniciar_sesion).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Registrarse", 
                    command=self.registrar_usuario).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Recuperar Contraseña", 
                    command=self.mostrar_restablecer_contrasena).pack(side="left", padx=10)

    # ... (Resto del código con todas las funciones implementadas)

if __name__ == "__main__":
    root = ctk.CTk()
    app = GestionStock(root)
    root.mainloop()
