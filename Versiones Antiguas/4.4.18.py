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
        
        if self.margen_ganancia < MARGEN_MINIMO:
            raise ValueError(f"Margen mínimo no alcanzado ({self.margen_ganancia:.1f}% < {MARGEN_MINIMO}%)")

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

    def _maximizar_ventana(self):
        sistema = platform.system()
        try:
            if sistema == "Windows":
                self.root.state('zoomed')
            else:
                self.root.attributes('-zoomed', True)
        except Exception:
            self.root.geometry("1200x800")

    def _crear_superusuario(self):
        if not any(u.usuario == "super" for u in self.usuarios):
            super_user = Usuario("super", "admin123", "clave_super", "super")
            self.usuarios.append(super_user)
            self.guardar_datos()

    def centrar_ventana(self, ventana, ancho=400, alto=300):
        ventana.update_idletasks()
        pantalla_ancho = ventana.winfo_screenwidth()
        pantalla_alto = ventana.winfo_screenheight()
        x = (pantalla_ancho - ancho) // 2
        y = (pantalla_alto - alto) // 2
        ventana.geometry(f'{ancho}x{alto}+{x}+{y}')

    def cargar_datos(self):
        try:
            with open(ARCHIVO_USUARIOS, "r") as file:
                usuarios_data = json.load(file)
                self.usuarios = [Usuario(**user) for user in usuarios_data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.usuarios = []

        try:
            with open(ARCHIVO_PRODUCTOS, 'r') as f:
                productos_data = json.load(f)
                self.productos = []
                for p in productos_data:
                    try:
                        self.productos.append(Producto(**p))
                    except ValueError as e:
                        print(f"Error en producto: {str(e)}")
        except (FileNotFoundError, json.JSONDecodeError):
            self.productos = []

        try:
            with open(ARCHIVO_VENTAS, 'r') as f:
                self.ventas = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.ventas = []

        try:
            with open(ARCHIVO_PROVEEDORES, 'r') as f:
                self.proveedores = [Proveedor(**p) for p in json.load(f)]
        except (FileNotFoundError, json.JSONDecodeError):
            self.proveedores = []

    def guardar_datos(self):
        try:
            with open(ARCHIVO_USUARIOS, "w") as file:
                usuarios_data = [{
                    "usuario": u.usuario,
                    "contrasena": u.contrasena,
                    "clave_recuperacion": u.clave_recuperacion,
                    "rol": u.rol
                } for u in self.usuarios]
                json.dump(usuarios_data, file, indent=4)

            with open(ARCHIVO_PRODUCTOS, 'w') as f:
                json.dump([vars(p) for p in self.productos], f, indent=4)
            
            with open(ARCHIVO_VENTAS, 'w') as f:
                json.dump(self.ventas, f, indent=4)
            
            with open(ARCHIVO_PROVEEDORES, 'w') as f:
                json.dump([vars(p) for p in self.proveedores], f, indent=4)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")

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
        
        self.entries_login = []
        for label, widget in campos:
            ctk.CTkLabel(self.login_window, text=label).pack(pady=5)
            widget.pack(pady=5)
            self.entries_login.append(widget)
        
        self.entries_login[2].set("Normal")

        btn_frame = ctk.CTkFrame(self.login_window)
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="Iniciar Sesión", command=self.iniciar_sesion).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Registrarse", command=self.registrar_usuario).pack(side="left", padx=10)

    def iniciar_sesion(self):
        usuario = self.entries_login[0].get()
        contrasena = self.entries_login[1].get()
        rol = self.entries_login[2].get().lower()

        # Verificar superusuario
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
                    and u.rol == rol), None)
        
        if user:
            self.current_user = user
            self.login_window.destroy()
            self.mostrar_interfaz_principal()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    def registrar_usuario(self):
        reg_window = ctk.CTkToplevel(self.login_window)
        reg_window.title("Registro de Usuario")
        self.centrar_ventana(reg_window, 300, 350)

        campos = [
            ("Usuario:", ctk.CTkEntry(reg_window)),
            ("Contraseña:", ctk.CTkEntry(reg_window, show="*")),
            ("Confirmar:", ctk.CTkEntry(reg_window, show="*")),
            ("Clave Recup.:", ctk.CTkEntry(reg_window)),
            ("Rol:", ctk.CTkComboBox(reg_window, values=["Normal", "Admin"]))
        ]
        
        entries = []
        for i, (label, widget) in enumerate(campos):
            ctk.CTkLabel(reg_window, text=label).grid(row=i, column=0, padx=5, pady=5)
            widget.grid(row=i, column=1, padx=5, pady=5)
            entries.append(widget)
        
        ctk.CTkButton(reg_window, text="Registrar", 
                     command=lambda: self._procesar_registro(entries)).grid(row=5, columnspan=2, pady=10)

    def _procesar_registro(self, entries):
        usuario = entries[0].get()
        contrasena = entries[1].get()
        confirmacion = entries[2].get()
        clave = entries[3].get()
        rol = entries[4].get().lower()

        if not all([usuario, contrasena, confirmacion, clave]):
            messagebox.showerror("Error", "Complete todos los campos")
            return
            
        if contrasena != confirmacion:
            messagebox.showerror("Error", "Contraseñas no coinciden")
            return
            
        if any(u.usuario == usuario for u in self.usuarios):
            messagebox.showerror("Error", "Usuario ya existe")
            return

        nuevo_usuario = Usuario(
            usuario=usuario,
            contrasena=contrasena,
            clave_recuperacion=clave,
            rol=rol
        )
        
        self.usuarios.append(nuevo_usuario)
        self.guardar_datos()
        messagebox.showinfo("Éxito", "Usuario registrado")
        entries[0].master.destroy()

    def mostrar_interfaz_principal(self):
        if self.toolbar:
            self.toolbar.destroy()
        if self.notebook:
            self.notebook.destroy()

        self.root.deiconify()
        self.root.title(f"Gestión de Stock - {self.current_user.usuario}")
        
        # Barra de herramientas
        self.toolbar = ctk.CTkFrame(self.root, height=40)
        self.toolbar.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(self.toolbar, text=f"Usuario: {self.current_user.usuario} ({self.current_user.rol})").pack(side="left", padx=10)
        ctk.CTkButton(self.toolbar, text="Cerrar Sesión", command=self.cerrar_sesion).pack(side="right", padx=10)

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.crear_pestana_ventas()
        self.crear_pestana_stock()
        
        if self.current_user.rol in ["admin", "super"]:
            self.crear_pestana_proveedores()
        
        if self.current_user.rol == "super":
            self.crear_pestana_usuarios()

    def crear_pestana_ventas(self):
        self.tab_ventas = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_ventas, text='Ventas')
        
        container = ctk.CTkFrame(self.tab_ventas, fg_color="transparent")
        container.pack(expand=True, fill="both")
        
        # ... (implementación completa de la pestaña de ventas del código anterior)

    # ... (implementar el resto de métodos para otras pestañas)

    def cerrar_sesion(self):
        self.guardar_datos()
        self.toolbar.destroy()
        self.notebook.destroy()
        self.root.withdraw()
        self.mostrar_login()

    def cerrar_aplicacion(self):
        self.guardar_datos()
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = GestionStock(root)
    root.mainloop()
