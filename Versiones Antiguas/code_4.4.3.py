import sys
import json
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import logging
import hashlib
import secrets

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ARCHIVO_PRODUCTOS = "productos.json"
ARCHIVO_VENTAS = "ventas.json"
ARCHIVO_PROVEEDORES = "proveedores.json"
ARCHIVO_USUARIOS = "usuarios.json"
MARGEN_MINIMO = 20

class Usuario:
    def __init__(self, usuario, contrasena, clave_recuperacion, rol="normal"):
        self.usuario = usuario
        self.contrasena = self._hash_contrasena(contrasena)
        self.clave_recuperacion = clave_recuperacion
        self.rol = rol  # 'admin' or 'normal'

    @staticmethod
    def _hash_contrasena(contrasena):
        return hashlib.sha256(contrasena.encode()).hexdigest()

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
        self.usuarios = []
        self.product_frames = {}
        self.auto_repeat_delay = 100
        self.auto_repeat_id = None
        self.current_user = None  # Keep track of the logged-in user
        
        self.cargar_datos()
        self.login_screen()
        
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

    def guardar_datos(self):
        with open(ARCHIVO_PRODUCTOS, "w") as file:
            json.dump(self.productos, file, indent=4)

        with open(ARCHIVO_VENTAS, "w") as file:
            json.dump(self.ventas, file, indent=4)

        with open(ARCHIVO_PROVEEDORES, "w") as file:
            json.dump(self.proveedores, file, indent=4)

        with open(ARCHIVO_USUARIOS, "w") as file:
            usuarios_data = [{"usuario": u.usuario, "contrasena": u.contrasena, "clave_recuperacion": u.clave_recuperacion, "rol": u.rol} for u in self.usuarios]
            json.dump(usuarios_data, file, indent=4)

    def login_screen(self):
        login_window = ctk.CTkToplevel(self.root)
        login_window.title("Iniciar Sesión")
        login_window.geometry("300x200")
        
        ctk.CTkLabel(login_window, text="Usuario").pack(pady=5)
        username_entry = ctk.CTkEntry(login_window)
        username_entry.pack(pady=5)
        
        ctk.CTkLabel(login_window, text="Contraseña").pack(pady=5)
        password_entry = ctk.CTkEntry(login_window, show="*")
        password_entry.pack(pady=5)
        
        def login():
            usuario = username_entry.get()
            contrasena = password_entry.get()
            user = self.autenticar_usuario(usuario, contrasena)
            if user:
                login_window.destroy()
                self.current_user = user
                self.setup_main_interface()
            else:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")
        
        ctk.CTkButton(login_window, text="Iniciar Sesión", command=login).pack(pady=20)

    def autenticar_usuario(self, usuario, contrasena):
        hashed_contrasena = Usuario._hash_contrasena(contrasena)
        for user in self.usuarios:
            if user.usuario == usuario and user.contrasena == hashed_contrasena:
                return user
        return None

    def setup_main_interface(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        self.crear_pestana_ventas()
        self.crear_pestana_stock()
        self.crear_pestana_analisis()
        self.crear_pestana_historial()
        self.crear_pestana_proveedores()
        self.crear_pestana_usuarios()

        if self.current_user.rol != 'admin':
            self.notebook.tab(self.tab_usuarios, state='disabled')

    def crear_pestana_usuarios(self):
        self.tab_usuarios = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_usuarios, text='Usuarios')
        
        container = ctk.CTkFrame(self.tab_usuarios, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        gestion_frame = ctk.CTkFrame(container, corner_radius=10, fg_color="#2b2b2b")
        gestion_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(gestion_frame, text="Registro de Usuario").grid(row=0, column=0, columnspan=3, pady=5)
        campos = ["Usuario:", "Contraseña:", "Clave de Recuperación:", "Rol:"]
        self.entries_usuario = []
        for i, label in enumerate(campos):
            ctk.CTkLabel(gestion_frame, text=label).grid(row=i+1, column=0, padx=5, pady=5)
            if label == "Rol:":
                entry = ctk.CTkComboBox(gestion_frame, values=["admin", "normal"], state='readonly')
                entry.set("normal")
            else:
                entry = ctk.CTkEntry(gestion_frame, width=250, show='*' if i > 0 else '')
            entry.grid(row=i+1, column=1, padx=5, pady=5)
            self.entries_usuario.append(entry)
        
        ctk.CTkButton(gestion_frame, text="Crear Usuario", command=self.crear_usuario).grid(row=5, column=0, columnspan=2, pady=10)
        ctk.CTkButton(gestion_frame, text="Buscar Usuario", command=self.buscar_usuario).grid(row=5, column=2, pady=10)

        lista_frame = ctk.CTkFrame(container, corner_radius=10, fg_color="#2b2b2b")
        lista_frame.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(lista_frame, text="Usuarios Registrados", font=("Arial", 14, "bold")).pack(pady=5)
        self.scroll_usuarios = ctk.CTkScrollableFrame(lista_frame, fg_color="#333333")
        self.scroll_usuarios.pack(fill="both", expand=True, padx=5, pady=5)
        self.actualizar_lista_usuarios()

    def crear_usuario(self):
        usuario, contrasena, clave_recuperacion, rol = [entry.get() for entry in self.entries_usuario]
        if all([usuario, contrasena, clave_recuperacion]):
            if self.current_user.rol != 'admin' and rol == 'admin':
                messagebox.showerror("Permiso Denegado", "Solo los administradores pueden crear otros administradores.")
                return
            nuevo_usuario = Usuario(usuario, contrasena, clave_recuperacion, rol)
            self.usuarios.append(nuevo_usuario)
            self.guardar_datos()
            self.actualizar_lista_usuarios()
            messagebox.showinfo("Éxito", "Usuario creado correctamente")
            self.limpiar_entradas_usuario()
        else:
            messagebox.showerror("Error", "Todos los campos son obligatorios")

    def buscar_usuario(self):
        usuario = messagebox.askstring("Buscar Usuario", "Ingrese el nombre de usuario:")
        if usuario:
            for user in self.usuarios:
                if user.usuario == usuario:
                    if self.current_user.rol == 'admin':
                        messagebox.showinfo("Usuario Encontrado", f"Rol: {user.rol}\nClave de Recuperación: {user.clave_recuperacion}")
                    else:
                        messagebox.showinfo("Usuario Encontrado", "Información de usuario encontrada.")
                    return
            messagebox.showerror("Error", "Usuario no encontrado")

    def modificar_usuario(self, usuario_actual):
        pass

    def eliminar_usuario(self, usuario_actual):
        if self.current_user.rol == 'admin':
            self.usuarios = [u for u in self.usuarios if u.usuario != usuario_actual]
            self.guardar_datos()
            self.actualizar_lista_usuarios()
            messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
        else:
            messagebox.showerror("Permiso Denegado", "Solo los administradores pueden eliminar usuarios.")

    def actualizar_lista_usuarios(self):
        for widget in self.scroll_usuarios.winfo_children():
            widget.destroy()

        for usuario in self.usuarios:
            frame = ctk.CTkFrame(self.scroll_usuarios, corner_radius=5, fg_color="#404040")
            frame.pack(fill="x", pady=2, padx=5)

            ctk.CTkLabel(frame, text=usuario.usuario, width=150, anchor="w").pack(side="left", padx=5)
            if self.current_user.rol == 'admin':
                ctk.CTkButton(frame, text="Modificar", command=lambda u=usuario: self.modificar_usuario(u.usuario)).pack(side="left", padx=5)
                ctk.CTkButton(frame, text="Eliminar", command=lambda u=usuario: self.eliminar_usuario(u.usuario)).pack(side="left", padx=5)

    def limpiar_entradas_usuario(self):
        for entry in self.entries_usuario:
            if isinstance(entry, ctk.CTkComboBox):
                entry.set("normal")
            else:
                entry.delete(0, 'end')

if __name__ == "__main__":
    root = ctk.CTk()
    app = GestionStock(root)
    root.mainloop()
