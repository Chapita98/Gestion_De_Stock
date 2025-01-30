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
        except (FileNotFoundError, json.JSONDecodeError):
            self.productos = []

        try:
            with open(ARCHIVO_VENTAS, "r") as file:
                self.ventas = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.ventas = []

        try:
            with open(ARCHIVO_PROVEEDORES, "r") as file:
                self.proveedores = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.proveedores = []

        try:
            with open(ARCHIVO_USUARIOS, "r") as file:
                usuarios_data = json.load(file)
                self.usuarios = [Usuario(**user) for user in usuarios_data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.usuarios = []

        try:
            with open(ARCHIVO_HISTORIAL, "r") as file:
                self.historial = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.historial = []

    def guardar_datos(self):
        try:
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
        except Exception as e:
            logging.error(f"Error al guardar datos: {str(e)}")

    # -------------------------------
    # Funciones de interfaz (CORREGIDAS)
    # -------------------------------
    def mostrar_login(self):
        self.login_window = ctk.CTkToplevel(self.root)
        self.login_window.title("Inicio de Sesión")
        self.login_window.geometry("400x400")
        self.login_window.grab_set()

        # Frame principal
        main_frame = ctk.CTkFrame(self.login_window)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Campos de entrada
        campos = [
            ("Usuario:", ctk.CTkEntry(main_frame)),
            ("Contraseña:", ctk.CTkEntry(main_frame, show="*")),
            ("Rol:", ctk.CTkComboBox(main_frame, 
                                   values=["admin", "normal"], 
                                   state="readonly"))
        ]

        self.entries = []
        for label, widget in campos:
            ctk.CTkLabel(main_frame, text=label).pack(pady=5)
            widget.pack(pady=5)
            self.entries.append(widget)
        
        self.entries[2].set("normal")  # Establecer valor por defecto para rol

        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Iniciar Sesión", 
                    command=self.iniciar_sesion).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Registrarse", 
                    command=self.registrar_usuario).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Recuperar Contraseña", 
                    command=self.mostrar_restablecer_contrasena).pack(side="left", padx=5)

    def iniciar_sesion(self):
        usuario = self.entries[0].get()
        contrasena = self.entries[1].get()
        rol = self.entries[2].get()

        user = next((u for u in self.usuarios if u.usuario == usuario 
                    and u.contrasena == Usuario._hash_contrasena(contrasena)
                    and u.rol == rol), None)
        
        if user:
            self.current_user = user
            self.login_window.destroy()
            self.mostrar_interfaz_principal()
            self.registrar_actividad("Inicio de sesión exitoso")
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")
            self.registrar_actividad("Intento fallido de inicio de sesión")

    def registrar_usuario(self):
        usuario = self.entries[0].get()
        contrasena = self.entries[1].get()
        rol = self.entries[2].get()

        if any(u.usuario == usuario for u in self.usuarios):
            messagebox.showerror("Error", "El usuario ya existe")
            return

        if not all([usuario, contrasena, rol]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        nuevo_usuario = Usuario(usuario, contrasena, "clave_temp", rol)
        self.usuarios.append(nuevo_usuario)
        self.guardar_datos()
        messagebox.showinfo("Éxito", "Usuario registrado correctamente")
        self.registrar_actividad(f"Registro de nuevo usuario: {usuario}")

    def mostrar_restablecer_contrasena(self):
        ventana = ctk.CTkToplevel(self.root)
        ventana.title("Recuperar Contraseña")
        ventana.geometry("300x250")

        campos = [
            ("Usuario:", ctk.CTkEntry(ventana)),
            ("Clave de Recuperación:", ctk.CTkEntry(ventana)),
            ("Nueva Contraseña:", ctk.CTkEntry(ventana, show="*"))
        ]

        entries = []
        for label, widget in campos:
            ctk.CTkLabel(ventana, text=label).pack(pady=5)
            widget.pack(pady=5)
            entries.append(widget)

        def confirmar():
            usuario = entries[0].get()
            clave = entries[1].get()
            nueva_contrasena = entries[2].get()

            user = next((u for u in self.usuarios 
                        if u.usuario == usuario 
                        and u.clave_recuperacion == clave), None)
            
            if user:
                user.contrasena = Usuario._hash_contrasena(nueva_contrasena)
                self.guardar_datos()
                messagebox.showinfo("Éxito", "Contraseña actualizada")
                ventana.destroy()
                self.registrar_actividad(f"Contraseña actualizada para: {usuario}")
            else:
                messagebox.showerror("Error", "Datos inválidos")

        ctk.CTkButton(ventana, text="Confirmar", command=confirmar).pack(pady=10)

    def mostrar_interfaz_principal(self):
        self.root.deiconify()
        self.root.title(f"Gestión de Stock - {self.current_user.usuario}")

        # Barra de herramientas
        toolbar = ctk.CTkFrame(self.root)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(toolbar, 
                    text="Cerrar Sesión", 
                    command=self.cerrar_sesion).pack(side="right", padx=5)

        # Notebook principal
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        
        # Implementar aquí las demás pestañas según necesidad

    def cerrar_sesion(self):
        self.guardar_datos()
        self.notebook.destroy()
        self.current_user = None
        self.root.withdraw()
        self.mostrar_login()
        self.registrar_actividad("Cierre de sesión")

    def cerrar_aplicacion(self):
        self.guardar_datos()
        self.root.destroy()

    # -------------------------------
    # Funciones adicionales
    # -------------------------------
    def registrar_actividad(self, accion):
        registro = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "usuario": self.current_user.usuario if self.current_user else "Sistema",
            "accion": accion
        }
        self.historial.append(registro)
        self.guardar_datos()

if __name__ == "__main__":
    root = ctk.CTk()
    app = GestionStock(root)
    root.mainloop()
