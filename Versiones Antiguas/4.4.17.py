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
        
        # Validación de margen mínimo
        if self.margen_ganancia < MARGEN_MINIMO:
            raise ValueError(f"Margen de ganancia insuficiente ({self.margen_ganancia:.1f}% < {MARGEN_MINIMO}%)")

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
        """Crea el usuario super si no existe"""
        super_user_exists = any(u.usuario == "super" for u in self.usuarios)
        
        if not super_user_exists:
            super_user = Usuario(
                usuario="super",
                contrasena="admin123",
                clave_recuperacion="clave_super",
                rol="super"
            )
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

    def cargar_datos(self):
        # Cargar usuarios con creación de archivo si no existe
        try:
            with open(ARCHIVO_USUARIOS, "r") as file:
                usuarios_data = json.load(file)
                self.usuarios = [Usuario(**user) for user in usuarios_data]
        except FileNotFoundError:
            with open(ARCHIVO_USUARIOS, "w") as file:
                json.dump([], file)
            self.usuarios = []
        except json.JSONDecodeError:
            messagebox.showerror("Error", f"Error en formato de {ARCHIVO_USUARIOS}")
            self.usuarios = []

        # Cargar productos con manejo de errores mejorado
        try:
            with open(ARCHIVO_PRODUCTOS, 'r') as f:
                productos_data = json.load(f)
                self.productos = []
                for p in productos_data:
                    try:
                        self.productos.append(Producto(**p))
                    except ValueError as e:
                        print(f"Producto inválido {p['nombre']}: {str(e)}")
        except FileNotFoundError:
            with open(ARCHIVO_PRODUCTOS, 'w') as f:
                json.dump([], f)
            self.productos = []
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando productos: {str(e)}")
            self.productos = []

        # Cargar ventas
        try:
            with open(ARCHIVO_VENTAS, 'r') as f:
                self.ventas = json.load(f)
        except FileNotFoundError:
            with open(ARCHIVO_VENTAS, 'w') as f:
                json.dump([], f)
            self.ventas = []

        # Cargar proveedores
        try:
            with open(ARCHIVO_PROVEEDORES, 'r') as f:
                self.proveedores = [Proveedor(**p) for p in json.load(f)]
        except FileNotFoundError:
            with open(ARCHIVO_PROVEEDORES, 'w') as f:
                json.dump([], f)
            self.proveedores = []

    def crear_pestana_ventas(self):
        self.tab_ventas = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_ventas, text='Realizar Ventas')
        
        container = ctk.CTkFrame(self.tab_ventas, fg_color="transparent")
        container.pack(expand=True, fill="both")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        center_frame = ctk.CTkFrame(container, fg_color="transparent")
        center_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        center_frame.grid_rowconfigure(0, weight=1)
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_columnconfigure(1, weight=1)
        
        # Frame de venta
        venta_frame = ctk.CTkFrame(center_frame, corner_radius=10)
        venta_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(venta_frame, text="Nombre del Producto:").grid(row=0, column=0, pady=5, padx=10, sticky="w")
        self.venta_nombre_entry = ctk.CTkEntry(venta_frame, width=250)
        self.venta_nombre_entry.grid(row=0, column=1, pady=5, padx=10, sticky="ew")
        
        ctk.CTkLabel(venta_frame, text="Cantidad:").grid(row=1, column=0, pady=5, padx=10, sticky="w")
        self.venta_cantidad_entry = ctk.CTkEntry(venta_frame, width=250)
        self.venta_cantidad_entry.grid(row=1, column=1, pady=5, padx=10, sticky="ew")
        
        ctk.CTkButton(venta_frame, text="Realizar Venta", command=self.realizar_venta).grid(row=2, column=0, columnspan=2, pady=10)

        # Frame de lista de precios con scrollbar
        precios_frame = ctk.CTkFrame(center_frame, corner_radius=10)
        precios_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(precios_frame, text="Lista de Precios", font=("Arial", 14, "bold")).pack(pady=5)
        
        # Contenedor para Treeview y Scrollbar
        tree_container = ctk.CTkFrame(precios_frame)
        tree_container.pack(padx=10, pady=10, fill='both', expand=True)
        
        self.tree = ttk.Treeview(tree_container, columns=('Nombre', 'Precio', 'Stock'), show='headings', height=15)
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)
        
        self.tree.heading('Nombre', text='Nombre')
        self.tree.heading('Precio', text='Precio')
        self.tree.heading('Stock', text='Stock')
        self.tree.column('Nombre', width=200)
        self.tree.column('Precio', width=100)
        self.tree.column('Stock', width=80)
        
        self.actualizar_lista_precios()

    def actualizar_lista_precios(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for producto in self.productos:
            stock_color = 'red' if producto.stock < producto.stock_minimo else 'black'
            self.tree.insert('', 'end', values=(
                producto.nombre, 
                f"${producto.precio:.2f}", 
                f"{producto.stock} ({producto.stock_minimo})"
            ))
            self.tree.tag_configure(stock_color, foreground=stock_color)

    def realizar_venta(self):
        nombre = self.venta_nombre_entry.get()
        cantidad = self.venta_cantidad_entry.get()
        
        if not nombre or not cantidad:
            messagebox.showerror("Error", "Complete todos los campos")
            return
        
        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida")
            return
            
        producto = next((p for p in self.productos if p.nombre.lower() == nombre.lower()), None)
        
        if not producto:
            messagebox.showerror("Error", "Producto no encontrado")
            return
            
        if producto.stock < cantidad:
            messagebox.showerror("Error", f"Stock insuficiente. Disponible: {producto.stock}")
            return
            
        producto.stock -= cantidad
        total = cantidad * producto.precio
        venta = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "producto": producto.nombre,
            "cantidad": cantidad,
            "total": total
        }
        self.ventas.append(venta)
        
        self.guardar_datos()
        self.actualizar_lista_precios()
        messagebox.showinfo("Éxito", f"Venta realizada!\nTotal: ${total:.2f}")
        
        self.venta_nombre_entry.delete(0, 'end')
        self.venta_cantidad_entry.delete(0, 'end')

    # ... (resto de métodos permanecen iguales)

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
            messagebox.showerror("Error", f"Error guardando datos: {str(e)}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = GestionStock(root)
    root.mainloop()
