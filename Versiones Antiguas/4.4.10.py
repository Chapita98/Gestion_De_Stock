# gestion_stock.py
import json
import platform
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, ttk
import logging
import hashlib

# Configuración inicial
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
ARCHIVO_USUARIOS = "usuarios.json"
ARCHIVO_PRODUCTOS = "productos.json"

class Usuario:
    def __init__(self, usuario, contrasena, clave_recuperacion, rol="normal"):
        self.usuario = usuario
        self.contrasena = self._hash_contrasena(contrasena)
        self.clave_recuperacion = clave_recuperacion
        self.rol = rol.lower()

    @staticmethod
    def _hash_contrasena(contrasena):
        return hashlib.sha256(contrasena.encode()).hexdigest()

class GestionStock:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Stock")
        self.root.withdraw()
        
        self._maximizar_ventana()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.usuarios = []
        self.productos = []
        self.current_user = None
        
        self._crear_superusuario()
        self.cargar_datos()
        self.mostrar_login()
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

    def _crear_superusuario(self):
        """Crea superusuario si no existe"""
        super_user = Usuario("super", "admin123", "clave_super", "super")
        if not any(u.usuario == "super" for u in self.usuarios):
            self.usuarios.append(super_user)
            self.guardar_datos()

    def _maximizar_ventana(self):
        sistema = platform.system()
        try:
            if sistema == "Windows":
                self.root.state('zoomed')
            else:
                self.root.attributes('-zoomed', True)
        except:
            self.root.geometry("1200x800")

    def cargar_datos(self):
        try:
            with open(ARCHIVO_USUARIOS, "r") as file:
                usuarios_data = json.load(file)
                self.usuarios = [Usuario(**user) for user in usuarios_data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.usuarios = []

        try:
            with open(ARCHIVO_PRODUCTOS, "r") as file:
                self.productos = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.productos = []

    def guardar_datos(self):
        with open(ARCHIVO_USUARIOS, "w") as file:
            usuarios_data = [{"usuario": u.usuario, 
                            "contrasena": u.contrasena, 
                            "clave_recuperacion": u.clave_recuperacion, 
                            "rol": u.rol} for u in self.usuarios]
            json.dump(usuarios_data, file, indent=4)

    def centrar_ventana(self, ventana, ancho=400, alto=300):
        ventana.update_idletasks()
        pantalla_ancho = ventana.winfo_screenwidth()
        pantalla_alto = ventana.winfo_screenheight()
        x = (pantalla_ancho - ancho) // 2
        y = (pantalla_alto - alto) // 2
        ventana.geometry(f'{ancho}x{alto}+{x}+{y}')

    def mostrar_login(self):
        self.login_window = ctk.CTkToplevel(self.root)
        self.login_window.title("Inicio de Sesión")
        self.centrar_ventana(self.login_window)
        
        # Textos con mayúscula inicial
        campos = [
            ("Usuario:", ctk.CTkEntry(self.login_window)),
            ("Contraseña:", ctk.CTkEntry(self.login_window, show="*")),
            ("Rol:", ctk.CTkComboBox(self.login_window, 
                                   values=["Normal", "Admin"], 
                                   state="readonly"))
        ]
        
        self.entries = []
        for label, widget in campos:
            ctk.CTkLabel(self.login_window, text=label).pack(pady=5)
            widget.pack(pady=5)
            self.entries.append(widget)
        
        self.entries[2].set("Normal")

        btn_frame = ctk.CTkFrame(self.login_window)
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Iniciar Sesión", command=self.iniciar_sesion).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Registrarse", command=self.registrar_usuario).pack(side="left", padx=10)

    def iniciar_sesion(self):
        usuario = self.entries[0].get()
        contrasena = self.entries[1].get()
        rol = self.entries[2].get().lower()

        user = next((u for u in self.usuarios 
                    if u.usuario == usuario 
                    and u.contrasena == Usuario._hash_contrasena(contrasena)
                    and u.rol == rol), None)
        
        if user:
            self.current_user = user
            self.login_window.destroy()
            self.mostrar_interfaz_principal()
        else:
            messagebox.showerror("Error", "Credenciales inválidas")

    def mostrar_interfaz_principal(self):
        self.root.deiconify()
        
        # Barra de herramientas
        toolbar = ctk.CTkFrame(self.root, height=40)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(toolbar, text=f"Usuario: {self.current_user.usuario}").pack(side="left", padx=10)
        ctk.CTkButton(toolbar, text="Cerrar Sesión", command=self.cerrar_sesion).pack(side="right", padx=10)

        # Notebook principal
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.crear_pestana_productos()
        
        if self.current_user.rol in ["admin", "super"]:
            self.crear_pestana_usuarios()

    def crear_pestana_productos(self):
        tab = ctk.CTkFrame(self.notebook)
        self.notebook.add(tab, text="Productos")
        
        # Cabecera
        header = ctk.CTkFrame(tab)
        header.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(header, text="Nombre", width=200).pack(side="left")
        ctk.CTkLabel(header, text="Stock", width=100).pack(side="left")
        ctk.CTkLabel(header, text="Precio", width=100).pack(side="left")
        
        # Lista de productos
        scroll = ctk.CTkScrollableFrame(tab, height=400)
        scroll.pack(fill="both", expand=True)
        
        for producto in self.productos:
            row = ctk.CTkFrame(scroll)
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=producto["nombre"], width=200).pack(side="left")
            ctk.CTkLabel(row, text=producto["stock"], width=100).pack(side="left")
            ctk.CTkLabel(row, text=f"${producto["precio"]}", width=100).pack(side="left")

    def crear_pestana_usuarios(self):
        tab = ctk.CTkFrame(self.notebook)
        self.notebook.add(tab, text="Usuarios")
        
        scroll = ctk.CTkScrollableFrame(tab, height=400)
        scroll.pack(fill="both", expand=True)
        
        for usuario in self.usuarios:
            row = ctk.CTkFrame(scroll)
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=usuario.usuario, width=150).pack(side="left")
            ctk.CTkLabel(row, text=usuario.rol.capitalize(), width=100).pack(side="left")
            
            if self.current_user.rol == "super":
                ctk.CTkButton(row, text="Eliminar", width=80).pack(side="right")

    def registrar_usuario(self):
        usuario = self.entries[0].get()
        contrasena = self.entries[1].get()
        rol = self.entries[2].get().lower()

        # Solo superusuario puede crear admins
        if rol == "admin" and self.current_user.rol != "super":
            messagebox.showerror("Error", "Solo superusuarios pueden crear admins")
            return

        if any(u.usuario == usuario for u in self.usuarios):
            messagebox.showerror("Error", "Usuario ya existe")
            return

        nuevo_usuario = Usuario(usuario, contrasena, "clave_temp", rol)
        self.usuarios.append(nuevo_usuario)
        self.guardar_datos()
        messagebox.showinfo("Éxito", "Usuario registrado correctamente")

    def cerrar_sesion(self):
        self.guardar_datos()
        self.notebook.destroy()
        self.current_user = None
        self.root.withdraw()
        self.mostrar_login()

    def cerrar_aplicacion(self):
        self.guardar_datos()
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = GestionStock(root)
    root.mainloop()
