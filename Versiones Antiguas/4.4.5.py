import sys
import json
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, ttk
import logging
import hashlib

# Configuración inicial (sin cambios)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
ARCHIVO_PRODUCTOS = "productos.json"
ARCHIVO_VENTAS = "ventas.json"
ARCHIVO_PROVEEDORES = "proveedores.json"
ARCHIVO_USUARIOS = "usuarios.json"
ARCHIVO_HISTORIAL = "historial.json"  # Nueva
MARGEN_MINIMO = 20

# Clase Usuario (sin cambios)
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
        # ... (sin cambios hasta cargar_datos)
        self.cargar_datos()
        self.cargar_historial()  # Nueva
        self.mostrar_login()

    # --------------------------------------
    # FUNCIÓN 2: Validación de usuarios únicos
    # --------------------------------------
    def registrar_usuario(self):
        usuario = self.username_entry.get()
        # Verificar si el usuario ya existe
        if any(u.usuario == usuario for u in self.usuarios):
            messagebox.showerror("Error", "❌ El nombre de usuario ya está en uso")
            return
        # ... (resto del código de registro)

    # --------------------------------------
    # FUNCIÓN 3: Restablecer contraseña
    # --------------------------------------
    def mostrar_restablecer_contrasena(self):
        ventana = ctk.CTkToplevel(self.root)
        ventana.title("Restablecer Contraseña")
        ventana.geometry("300x200")

        campos = [
            ("Usuario:", ctk.CTkEntry),
            ("Clave de Recuperación:", ctk.CTkEntry),
            ("Nueva Contraseña:", ctk.CTkEntry(show="*"))
        ]

        entries = []
        for i, (label, widget) in enumerate(campos):
            ctk.CTkLabel(ventana, text=label).pack(pady=5)
            entry = widget(ventana)
            entry.pack(pady=5)
            entries.append(entry)

        def confirmar():
            usuario, clave, nueva_contrasena = [e.get() for e in entries]
            user = next((u for u in self.usuarios if u.usuario == usuario and u.clave_recuperacion == clave), None)
            if user:
                user.contrasena = Usuario._hash_contrasena(nueva_contrasena)
                self.guardar_datos()
                messagebox.showinfo("Éxito", "🔑 Contraseña actualizada correctamente")
                ventana.destroy()
            else:
                messagebox.showerror("Error", "Datos de recuperación inválidos")

        ctk.CTkButton(ventana, text="Confirmar", command=confirmar).pack(pady=10)

    # --------------------------------------
    # FUNCIÓN 5: Alertas de stock bajo
    # --------------------------------------
    def actualizar_lista_productos(self):
        for widget in self.scroll_productos.winfo_children():
            widget.destroy()

        for producto in self.productos:
            frame = ctk.CTkFrame(self.scroll_productos, fg_color="#404040")
            frame.pack(fill="x", pady=2, padx=5)

            # Alerta visual si el stock es bajo
            if producto["stock"] < MARGEN_MINIMO:
                ctk.CTkLabel(frame, text="⚠", text_color="#FFD700").pack(side="left", padx=5)
            
            ctk.CTkLabel(frame, text=producto["nombre"], width=150).pack(side="left")
            # ... (resto del código)

    # --------------------------------------
    # FUNCIÓN 7: Historial de actividad
    # --------------------------------------
    def cargar_historial(self):
        try:
            with open(ARCHIVO_HISTORIAL, "r") as file:
                self.historial = json.load(file)
        except FileNotFoundError:
            self.historial = []

    def registrar_actividad(self, accion):
        registro = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "usuario": self.current_user.usuario,
            "accion": accion
        }
        self.historial.append(registro)
        with open(ARCHIVO_HISTORIAL, "w") as file:
            json.dump(self.historial, file, indent=4)

    # Ejemplo de uso:
    def eliminar_usuario(self, usuario_actual):
        if self.current_user.rol == 'admin':
            self.usuarios = [u for u in self.usuarios if u.usuario != usuario_actual]
            self.registrar_actividad(f"Eliminó al usuario: {usuario_actual}")  # Registro
            # ... (resto del código)
