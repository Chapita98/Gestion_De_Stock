import sys
import json
import platform
import hashlib
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configuración de archivos
ARCHIVO_PRODUCTOS = "productos.json"
ARCHIVO_VENTAS = "ventas.json"
ARCHIVO_PROVEEDORES = "proveedores.json"
ARCHIVO_USUARIOS = "usuarios.json"
MARGEN_MINIMO = 20

# ------------------------- CLASES AUXILIARES -------------------------
class EditarUsuarioDialog(ctk.CTkToplevel):
    def __init__(self, parent, usuario, gestion_stock):
        super().__init__(parent)
        self.usuario = usuario
        self.gestion = gestion_stock
        self.title(f"Editar Usuario: {usuario.usuario}")
        
        campos = [
            ("Nueva Contraseña:", ctk.CTkEntry(self, show="*")),
            ("Confirmar Contraseña:", ctk.CTkEntry(self, show="*")),
            ("Rol:", ctk.CTkComboBox(self, values=["Normal", "Admin"], state="readonly"))
        ]
        
        self.entries = []
        for i, (label, widget) in enumerate(campos):
            ctk.CTkLabel(self, text=label).grid(row=i, column=0, padx=10, pady=5)
            widget.grid(row=i, column=1, padx=10, pady=5)
            self.entries.append(widget)
        
        self.entries[2].set(usuario.rol.capitalize())
        ctk.CTkButton(self, text="Guardar Cambios", command=self.guardar).grid(row=3, column=0, columnspan=2, pady=10)
    
    def guardar(self):
        nueva_pass = self.entries[0].get()
        confirm_pass = self.entries[1].get()
        nuevo_rol = self.entries[2].get().lower()
        
        if nueva_pass and nueva_pass != confirm_pass:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        
        if nueva_pass:
            self.usuario.contrasena = Usuario._hash_contrasena(nueva_pass)
        
        self.usuario.rol = nuevo_rol
        self.gestion.guardar_datos()
        self.destroy()

class Usuario:
    def __init__(self, usuario, contrasena, clave_recuperacion, rol="normal"):
        self.usuario = usuario
        self.contrasena = self._hash_contrasena(contrasena)
        self.clave_recuperacion = clave_recuperacion
        self.rol = rol.lower()

    @staticmethod
    def _hash_contrasena(contrasena):
        return hashlib.sha256(contrasena.encode()).hexdigest()

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
        if self.precio == 0:
            return 0
        return ((self.precio - self.costo) / self.precio) * 100

class Proveedor:
    def __init__(self, nombre, telefono, direccion):
        self.nombre = nombre
        self.telefono = telefono
        self.direccion = direccion

# ------------------------- CLASE PRINCIPAL -------------------------
class GestionStock:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Stock - Ferretería")
        self.root.withdraw()
        
        self.toolbar = None
        self.notebook = None
        self.current_user = None
        
        self._maximizar_ventana()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.usuarios = []
        self.productos = []
        self.ventas = []
        self.proveedores = []
        self.product_frames = {}
        self.auto_repeat_delay = 100
        self.auto_repeat_id = None
        
        self._crear_superusuario()
        self.cargar_datos()
        self.mostrar_login()
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

    def _crear_superusuario(self):
        if not any(u.usuario == "super" for u in self.usuarios):
            super_user = Usuario("super", "admin123", "clave_super", "super")
            self.usuarios.append(super_user)
            self.guardar_datos()

    def _maximizar_ventana(self):
        sistema = platform.system()
        try:
            if sistema == "Windows":
                self.root.state('zoomed')
            else:
                self.root.attributes('-zoomed', True)
        except Exception:
            self.root.geometry("1200x800")

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
        self.centrar_ventana(self.login_window, 400, 350)
        self.login_window.grab_set()

        campos = [
            ("Usuario:", ctk.CTkEntry(self.login_window)),
            ("Contraseña:", ctk.CTkEntry(self.login_window, show="*")),
            ("Rol:", ctk.CTkComboBox(self.login_window, values=["Normal", "Admin"], state="readonly"))
        ]
        
        self.entries = []
        for label, widget in campos:
            ctk.CTkLabel(self.login_window, text=label).pack(pady=5)
            widget.pack(pady=5)
            self.entries.append(widget)
        
        self.entries[2].set("Normal")

        btn_frame = ctk.CTkFrame(self.login_window)
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="Iniciar Sesión", command=self.iniciar_sesion).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Registrarse", command=self.registrar_usuario).pack(side="left", padx=10)

    def iniciar_sesion(self):
        usuario = self.entries[0].get()
        contrasena = self.entries[1].get()
        rol_seleccionado = self.entries[2].get().lower()

        if usuario == "super" and contrasena == "admin123":
            user = next((u for u in self.usuarios if u.usuario == "super"), None)
            if user:
                self.current_user = user
                self.login_window.destroy()
                self.mostrar_interfaz_principal()
                return

        user = next((u for u in self.usuarios 
                    if u.usuario == usuario 
                    and u.contrasena == Usuario._hash_contrasena(contrasena)
                    and u.rol == rol_seleccionado), None)
        
        if user:
            self.current_user = user
            self.login_window.destroy()
            self.mostrar_interfaz_principal()
        else:
            messagebox.showerror("Error", "Credenciales inválidas")

    def mostrar_interfaz_principal(self):
        if self.toolbar:
            self.toolbar.destroy()
        if self.notebook:
            self.notebook.destroy()

        self.root.deiconify()
        self._maximizar_ventana()
        self.root.title(f"Gestión de Stock - {self.current_user.usuario}")
        
        self.toolbar = ctk.CTkFrame(self.root, height=40)
        self.toolbar.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(self.toolbar, text=f"Usuario: {self.current_user.usuario}").pack(side="left", padx=10)
        ctk.CTkButton(self.toolbar, text="Cerrar Sesión", command=self.cerrar_sesion).pack(side="right", padx=10)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.crear_pestana_ventas()
        self.crear_pestana_stock()
        self.crear_pestana_analisis()
        self.crear_pestana_historial()
        
        if self.current_user.rol in ["admin", "super"]:
            self.crear_pestana_proveedores()
        
        if self.current_user.rol == "super":
            self.crear_pestana_usuarios()

    def cerrar_sesion(self):
        self.guardar_datos()
        if self.notebook:
            self.notebook.destroy()
            self.notebook = None
        if self.toolbar:
            self.toolbar.destroy()
            self.toolbar = None
        self.current_user = None
        self.root.withdraw()
        self.mostrar_login()

    def cargar_datos(self):
        try:
            with open(ARCHIVO_USUARIOS, "r") as file:
                usuarios_data = json.load(file)
                self.usuarios = [Usuario(**user) for user in usuarios_data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.usuarios = []

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

    def guardar_datos(self):
        with open(ARCHIVO_USUARIOS, "w") as file:
            usuarios_data = [{
                "usuario": u.usuario,
                "contrasena": u.contrasena,
                "clave_recuperacion": u.clave_recuperacion,
                "rol": u.rol
            } for u in self.usuarios]
            json.dump(usuarios_data, file, indent=4)

        with open(ARCHIVO_PRODUCTOS, 'w') as f:
            json.dump([vars(p) for p in self.productos], f)
        with open(ARCHIVO_VENTAS, 'w') as f:
            json.dump(self.ventas, f)
        with open(ARCHIVO_PROVEEDORES, 'w') as f:
            json.dump([vars(p) for p in self.proveedores], f)

    # ------------------------- PESTAÑA USUARIOS -------------------------
    def crear_pestana_ventas(self):
        self.tab_ventas = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_ventas, text='Realizar Ventas')
        
        container = ctk.CTkFrame(self.tab_ventas, fg_color="transparent")
        container.pack(expand=True, fill="both")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        
        center_frame = ctk.CTkFrame(container, fg_color="transparent")
        center_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        venta_frame = ctk.CTkFrame(center_frame, corner_radius=10, fg_color="#2b2b2b")
        venta_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)
        
        # Línea 377 corregida ▼
        ctk.CTkLabel(venta_frame, text="Nombre del Producto:").grid(row=0, column=0, pady=5, padx=10)
        self.venta_nombre_entry = ctk.CTkEntry(venta_frame, width=250)
        self.venta_nombre_entry.grid(row=0, column=1, pady=5, padx=10)
        
        ctk.CTkLabel(venta_frame, text="Cantidad:").grid(row=1, column=0, pady=5, padx=10)
        self.venta_cantidad_entry = ctk.CTkEntry(venta_frame, width=250)
        self.venta_cantidad_entry.grid(row=1, column=1, pady=5, padx=10)
        
        ctk.CTkButton(venta_frame, text="Realizar Venta", command=self.realizar_venta, width=200, fg_color="#1e6ba5").grid(row=2, column=0, columnspan=2, pady=10)

        precios_frame = ctk.CTkFrame(center_frame, corner_radius=10, fg_color="#2b2b2b")
        precios_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)
        
        ctk.CTkLabel(precios_frame, text="Lista de Precios", font=("Arial", 14, "bold"), text_color="#ffffff").pack(pady=5)
        
        self.scroll_precios = ctk.CTkScrollableFrame(precios_frame, height=400, fg_color="#333333")
        self.scroll_precios.pack(fill="both", expand=True, padx=5, pady=5)
        self.actualizar_lista_precios()

    def actualizar_lista_usuarios(self):
        for widget in self.scroll_usuarios.winfo_children():
            widget.destroy()
        
        for usuario in self.usuarios:
            frame = ctk.CTkFrame(self.scroll_usuarios, corner_radius=5, fg_color="#404040")
            frame.pack(fill="x", pady=2, padx=5)
            
            ctk.CTkLabel(frame, text=usuario.usuario, width=150).pack(side="left", padx=5)
            ctk.CTkLabel(frame, text=usuario.rol, width=100).pack(side="left", padx=5)
            
            btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
            btn_frame.pack(side="right", padx=5)
            
            if usuario.usuario != "super":
                ctk.CTkButton(btn_frame, text="Editar", width=80, fg_color="#1e6ba5",
                            command=lambda u=usuario: self.editar_usuario(u)).pack(side="left", padx=2)
                ctk.CTkButton(btn_frame, text="Eliminar", width=80, fg_color="#b30000",
                            command=lambda u=usuario: self.eliminar_usuario(u)).pack(side="left", padx=2)

    def agregar_usuario(self):
        datos = [entry.get() for entry in self.entries_usuarios]
        if not all(datos[:2]):
            messagebox.showerror("Error", "Usuario y contraseña son obligatorios")
            return
        
        rol = datos[2].lower() if datos[2] else "normal"
        
        if any(u.usuario == datos[0] for u in self.usuarios):
            messagebox.showerror("Error", "El usuario ya existe")
            return
        
        nuevo_usuario = Usuario(datos[0], datos[1], "clave_temp", rol)
        self.usuarios.append(nuevo_usuario)
        self.guardar_datos()
        self.actualizar_lista_usuarios()
        
        for entry in self.entries_usuarios:
            if isinstance(entry, ctk.CTkEntry):
                entry.delete(0, 'end')
            elif isinstance(entry, ctk.CTkComboBox):
                entry.set("Normal")

    def editar_usuario(self, usuario):
        dialog = EditarUsuarioDialog(self.root, usuario, self)
        dialog.grab_set()

    def eliminar_usuario(self, usuario):
        if usuario.usuario == "super":
            messagebox.showerror("Error", "No se puede eliminar al superusuario")
            return
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar usuario {usuario.usuario}?"):
            self.usuarios.remove(usuario)
            self.guardar_datos()
            self.actualizar_lista_usuarios()

    # ------------------------- OTRAS PESTAÑAS -------------------------
    def crear_pestana_ventas(self):
        self.tab_ventas = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_ventas, text='Realizar Ventas')
        
        container = ctk.CTkFrame(self.tab_ventas, fg_color="transparent")
        container.pack(expand=True, fill="both")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        
        center_frame = ctk.CTkFrame(container, fg_color="transparent")
        center_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        venta_frame = ctk.CTkFrame(center_frame, corner_radius=10, fg_color="#2b2b2b")
        venta_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)
        
        # Línea 377 corregida ▼
        ctk.CTkLabel(venta_frame, text="Nombre del Producto:").grid(row=0, column=0, pady=5, padx=10)
        self.venta_nombre_entry = ctk.CTkEntry(venta_frame, width=250)
        self.venta_nombre_entry.grid(row=0, column=1, pady=5, padx=10)
        
        ctk.CTkLabel(venta_frame, text="Cantidad:").grid(row=1, column=0, pady=5, padx=10)
        self.venta_cantidad_entry = ctk.CTkEntry(venta_frame, width=250)
        self.venta_cantidad_entry.grid(row=1, column=1, pady=5, padx=10)
        
        ctk.CTkButton(venta_frame, text="Realizar Venta", command=self.realizar_venta, width=200, fg_color="#1e6ba5").grid(row=2, column=0, columnspan=2, pady=10)

        precios_frame = ctk.CTkFrame(center_frame, corner_radius=10, fg_color="#2b2b2b")
        precios_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)
        
        ctk.CTkLabel(precios_frame, text="Lista de Precios", font=("Arial", 14, "bold"), text_color="#ffffff").pack(pady=5)
        
        self.scroll_precios = ctk.CTkScrollableFrame(precios_frame, height=400, fg_color="#333333")
        self.scroll_precios.pack(fill="both", expand=True, padx=5, pady=5)
        self.actualizar_lista_precios()
