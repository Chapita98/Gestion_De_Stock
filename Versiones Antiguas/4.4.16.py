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

# ========================= CLASES AUXILIARES =========================
class EditarUsuarioDialog(ctk.CTkToplevel):
    def __init__(self, parent, usuario, gestion_stock):
        super().__init__(parent)
        self.usuario = usuario
        self.gestion = gestion_stock
        self.title(f"Editar Usuario: {usuario.usuario}")
        
        # Configuración de la interfaz
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
        
        # Validaciones
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
        return ((self.precio - self.costo) / self.precio) * 100 if self.precio != 0 else 0

class Proveedor:
    def __init__(self, nombre, telefono, direccion):
        self.nombre = nombre
        self.telefono = telefono
        self.direccion = direccion

# ========================= CLASE PRINCIPAL =========================
class GestionStock:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Stock - Ferretería")
        self.root.withdraw()
        
        # Configuración inicial
        self._maximizar_ventana()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Datos
        self.usuarios = []
        self.productos = []
        self.ventas = []
        self.proveedores = []
        self.product_frames = {}
        
        # Inicialización
        self._crear_superusuario()
        self.cargar_datos()
        self.mostrar_login()
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

    # ------------------------- MÉTODOS BÁSICOS -------------------------
    def _crear_superusuario(self):
        if not any(u.usuario == "super" for u in self.usuarios):
            super_user = Usuario("super", "admin123", "clave_super", "super")
            self.usuarios.append(super_user)
            self.guardar_datos()

    def _maximizar_ventana(self):
        try:
            if platform.system() == "Windows":
                self.root.state('zoomed')
            else:
                self.root.attributes('-zoomed', True)
        except:
            self.root.geometry("1200x800")

    def centrar_ventana(self, ventana, ancho=400, alto=300):
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() - ancho) // 2
        y = (ventana.winfo_screenheight() - alto) // 2
        ventana.geometry(f'{ancho}x{alto}+{x}+{y}')

    # ------------------------- AUTENTICACIÓN -------------------------
    def mostrar_login(self):
        self.login_window = ctk.CTkToplevel(self.root)
        self.login_window.title("Inicio de Sesión")
        self.centrar_ventana(self.login_window, 400, 350)
        self.login_window.grab_set()

        # Campos de entrada
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

        # Botones
        btn_frame = ctk.CTkFrame(self.login_window)
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text="Iniciar Sesión", command=self.iniciar_sesion).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Registrarse", command=self.registrar_usuario).pack(side="left", padx=10)

    def iniciar_sesion(self):
        usuario = self.entries[0].get().strip()
        contrasena = self.entries[1].get().strip()
        rol = self.entries[2].get().lower()

        # Verificar superusuario
        if usuario == "super" and contrasena == "admin123":
            self.current_user = next((u for u in self.usuarios if u.usuario == "super"), None)
            if self.current_user:
                self.login_window.destroy()
                self.mostrar_interfaz_principal()
                return

        # Buscar usuario
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

    # ------------------------- INTERFAZ PRINCIPAL -------------------------
    def mostrar_interfaz_principal(self):
        # Limpiar elementos anteriores
        if hasattr(self, 'toolbar'): self.toolbar.destroy()
        if hasattr(self, 'notebook'): self.notebook.destroy()

        # Configurar ventana
        self.root.deiconify()
        self._maximizar_ventana()
        self.root.title(f"Gestión de Stock - {self.current_user.usuario}")
        
        # Barra de herramientas
        self.toolbar = ctk.CTkFrame(self.root, height=40)
        self.toolbar.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(self.toolbar, text=f"Usuario: {self.current_user.usuario}").pack(side="left", padx=10)
        ctk.CTkButton(self.toolbar, text="Cerrar Sesión", command=self.cerrar_sesion).pack(side="right", padx=10)

        # Notebook (pestañas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Crear pestañas
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
        self.notebook.destroy() if hasattr(self, 'notebook') else None
        self.toolbar.destroy() if hasattr(self, 'toolbar') else None
        self.current_user = None
        self.root.withdraw()
        self.mostrar_login()

    # ------------------------- MANEJO DE DATOS -------------------------
    def cargar_datos(self):
        try:
            with open(ARCHIVO_USUARIOS, "r") as f:
                self.usuarios = [Usuario(**u) for u in json.load(f)]
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
            pass

    def guardar_datos(self):
        with open(ARCHIVO_USUARIOS, "w") as f:
            json.dump([{
                "usuario": u.usuario,
                "contrasena": u.contrasena,
                "clave_recuperacion": u.clave_recuperacion,
                "rol": u.rol
            } for u in self.usuarios], f, indent=4)

        with open(ARCHIVO_PRODUCTOS, 'w') as f:
            json.dump([vars(p) for p in self.productos], f)
        with open(ARCHIVO_VENTAS, 'w') as f:
            json.dump(self.ventas, f)
        with open(ARCHIVO_PROVEEDORES, 'w') as f:
            json.dump([vars(p) for p in self.proveedores], f)

    # ------------------------- PESTAÑA VENTAS -------------------------
    def crear_pestana_ventas(self):
        self.tab_ventas = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_ventas, text='Realizar Ventas')
        
        # Contenedor principal
        container = ctk.CTkFrame(self.tab_ventas, fg_color="transparent")
        container.pack(expand=True, fill="both")
        
        # Sección de venta
        venta_frame = ctk.CTkFrame(container, corner_radius=10, fg_color="#2b2b2b")
        venta_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)
        
        # Campos de entrada
        ctk.CTkLabel(venta_frame, text="Nombre del Producto:").grid(row=0, column=0, pady=5, padx=10)
        self.venta_nombre_entry = ctk.CTkEntry(venta_frame, width=250)
        self.venta_nombre_entry.grid(row=0, column=1, pady=5, padx=10)
        
        ctk.CTkLabel(venta_frame, text="Cantidad:").grid(row=1, column=0, pady=5, padx=10)
        self.venta_cantidad_entry = ctk.CTkEntry(venta_frame, width=250)
        self.venta_cantidad_entry.grid(row=1, column=1, pady=5, padx=10)
        
        ctk.CTkButton(venta_frame, text="Realizar Venta", 
                    command=self.realizar_venta, width=200, fg_color="#1e6ba5").grid(row=2, column=0, columnspan=2, pady=10)

        # Lista de precios
        precios_frame = ctk.CTkFrame(container, corner_radius=10, fg_color="#2b2b2b")
        precios_frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)
        
        ctk.CTkLabel(precios_frame, text="Lista de Precios", 
                   font=("Arial", 14, "bold"), text_color="#ffffff").pack(pady=5)
        
        self.scroll_precios = ctk.CTkScrollableFrame(precios_frame, height=400, fg_color="#333333")
        self.scroll_precios.pack(fill="both", expand=True, padx=5, pady=5)
        self.actualizar_lista_precios()

    def realizar_venta(self):
        nombre = self.venta_nombre_entry.get().strip()
        cantidad = self.venta_cantidad_entry.get().strip()
        
        if not nombre or not cantidad:
            messagebox.showerror("Error", "Complete todos los campos")
            return

        try:
            cantidad = int(cantidad)
            for producto in self.productos:
                if producto.nombre.lower() == nombre.lower():
                    if producto.stock >= cantidad:
                        producto.stock -= cantidad
                        self.ventas.append({
                            "producto": producto.nombre,
                            "cantidad": cantidad,
                            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "total": producto.precio * cantidad
                        })
                        self.guardar_datos()
                        self.actualizar_lista_stock()
                        messagebox.showinfo("Éxito", f"Venta realizada. Stock actual: {producto.stock}")
                        self.venta_nombre_entry.delete(0, 'end')
                        self.venta_cantidad_entry.delete(0, 'end')
                        return
                    else:
                        messagebox.showerror("Error", f"Stock insuficiente de {nombre}")
                        return
            messagebox.showerror("Error", "Producto no encontrado")
        except ValueError:
            messagebox.showerror("Error", "Cantidad debe ser un número entero")

    # ------------------------- PESTAÑA STOCK -------------------------
    def crear_pestana_stock(self):
        self.tab_stock = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_stock, text='Gestión de Stock')
        
        # Alertas de stock bajo
        alertas_frame = ctk.CTkFrame(self.tab_stock, corner_radius=10, fg_color="#4a0000")
        alertas_frame.pack(pady=5, padx=10, fill='x')
        ctk.CTkLabel(alertas_frame, text="⚠️ Productos con Stock Bajo", 
                   font=("Arial", 12, "bold"), text_color="#ff6666").pack(pady=5)
        
        self.scroll_alertas = ctk.CTkScrollableFrame(alertas_frame, height=100, fg_color="#333333")
        self.scroll_alertas.pack(fill="both", expand=True, padx=5, pady=5)

        # Controles de inventario
        control_frame = ctk.CTkFrame(self.tab_stock, fg_color="#2b2b2b")
        control_frame.pack(pady=10, padx=10, fill='x')

        labels = ["Código:", "Nombre:", "Categoría:", "Costo:", "Precio:", "Stock:", "Alerta Mínima:"]
        self.entries_stock = []
        for i, label in enumerate(labels):
            ctk.CTkLabel(control_frame, text=label).grid(row=i//4, column=(i%4)*2, padx=5, pady=2)
            entry = ctk.CTkEntry(control_frame, width=120)
            entry.grid(row=i//4, column=(i%4)*2+1, padx=5, pady=2)
            self.entries_stock.append(entry)

        ctk.CTkButton(control_frame, text="Agregar Producto", 
                    command=self.agregar_producto, fg_color="#1e6ba5").grid(row=2, column=7, padx=10, pady=5, sticky='e')

        # Lista de inventario
        self.scrollable_stock_frame = ctk.CTkScrollableFrame(self.tab_stock, label_text="Inventario Actual", 
                                                           fg_color="#333333")
        self.scrollable_stock_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.actualizar_lista_stock()

    def agregar_producto(self):
        datos = [entry.get().strip() for entry in self.entries_stock]
        if not all(datos[:6]):
            messagebox.showerror("Error", "Complete los 6 primeros campos")
            return

        try:
            nuevo_producto = Producto(
                datos[0], datos[1], datos[2], datos[3], datos[4], datos[5],
                datos[6] if len(datos) > 6 else 5
            )
            
            if any(p.codigo == nuevo_producto.codigo for p in self.productos):
                messagebox.showerror("Error", "El código ya existe")
                return
            
            self.productos.append(nuevo_producto)
            self.guardar_datos()
            self.actualizar_lista_stock()
            for entry in self.entries_stock: entry.delete(0, 'end')
            messagebox.showinfo("Éxito", "Producto agregado")
        except ValueError:
            messagebox.showerror("Error", "Datos numéricos inválidos")

    # ------------------------- PESTAÑA USUARIOS -------------------------
    def crear_pestana_usuarios(self):
        self.tab_usuarios = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_usuarios, text='Administrar Usuarios')
        
        main_frame = ctk.CTkFrame(self.tab_usuarios, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Formulario de registro
        registro_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        registro_frame.pack(pady=10, padx=10, fill="x")

        campos = ["Usuario:", "Contraseña:", "Rol:"]
        self.entries_usuarios = []
        for i, texto in enumerate(campos):
            ctk.CTkLabel(registro_frame, text=texto).grid(row=0, column=i*2, padx=5, pady=5)
            if texto == "Rol:":
                entry = ctk.CTkComboBox(registro_frame, values=["Normal", "Admin"], state="readonly")
                entry.set("Normal")
            else:
                entry = ctk.CTkEntry(registro_frame, width=200)
            entry.grid(row=0, column=i*2+1, padx=5, pady=5)
            self.entries_usuarios.append(entry)

        ctk.CTkButton(registro_frame, text="Agregar Usuario", 
                    command=self.agregar_usuario, fg_color="#1e6ba5").grid(row=1, column=0, columnspan=6, pady=10)

        # Lista de usuarios
        lista_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        lista_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.scroll_usuarios = ctk.CTkScrollableFrame(lista_frame, fg_color="#333333")
        self.scroll_usuarios.pack(fill="both", expand=True, padx=5, pady=5)
        self.actualizar_lista_usuarios()

    # ------------------------- MÉTODOS ADICIONALES -------------------------
    def actualizar_lista_precios(self):
        for widget in self.scroll_precios.winfo_children():
            widget.destroy()
        
        for producto in sorted(self.productos, key=lambda p: p.nombre):
            frame = ctk.CTkFrame(self.scroll_precios, corner_radius=5, fg_color="#404040")
            frame.pack(fill='x', pady=2, padx=5)
            ctk.CTkLabel(frame, text=producto.nombre, width=200, anchor="w").pack(side='left', padx=5)
            ctk.CTkLabel(frame, text=f"${producto.precio:.2f}", width=100).pack(side='right', padx=5)

    def actualizar_lista_stock(self):
        for widget in self.scrollable_stock_frame.winfo_children():
            widget.destroy()
        
        for producto in self.productos:
            frame = ctk.CTkFrame(self.scrollable_stock_frame, corner_radius=5)
            frame.pack(fill='x', pady=2, padx=5)
            
            # Información del producto
            labels = {
                'codigo': ctk.CTkLabel(frame, text=producto.codigo, width=80),
                'nombre': ctk.CTkLabel(frame, text=producto.nombre, width=200),
                'categoria': ctk.CTkLabel(frame, text=producto.categoria, width=150),
                'stock': ctk.CTkLabel(frame, text=f"Stock: {producto.stock}", width=100),
                'alerta': ctk.CTkLabel(frame, text=f"Alerta: {producto.stock_minimo}", width=100)
            }
            
            for label in labels.values():
                label.pack(side='left', padx=5)

            # Controles
            btn_frame = ctk.CTkFrame(frame, fg_color='transparent')
            btn_frame.pack(side='right', padx=5)
            
            ctk.CTkButton(btn_frame, text="-", width=30, height=30, fg_color="#1e6ba5",
                        command=lambda p=producto: self.ajustar_stock(p, -1)).pack(side='left', padx=2)
            ctk.CTkButton(btn_frame, text="+", width=30, height=30, fg_color="#1e6ba5",
                        command=lambda p=producto: self.ajustar_stock(p, 1)).pack(side='left', padx=2)
            
            ctk.CTkButton(btn_frame, text="Fijar Alerta", width=80, fg_color="#1e6ba5",
                        command=lambda p=producto: self.fijar_alerta_stock(p)).pack(side='left', padx=2)
            ctk.CTkButton(btn_frame, text="Eliminar", width=80, fg_color="#b30000",
                        command=lambda p=producto: self.eliminar_producto(p)).pack(side='left', padx=2)

    def ajustar_stock(self, producto, incremento):
        nuevo_stock = producto.stock + incremento
        if nuevo_stock < 0: return
        producto.stock = nuevo_stock
        self.guardar_datos()
        self.actualizar_lista_stock()

    def fijar_alerta_stock(self, producto):
        dialogo = ctk.CTkInputDialog(text=f"Nuevo stock mínimo para {producto.nombre}:",
                                   title="Configurar Alerta")
        nuevo_minimo = dialogo.get_input()
        
        try:
            nuevo_minimo = int(nuevo_minimo)
            if nuevo_minimo < 0: raise ValueError
            producto.stock_minimo = nuevo_minimo
            self.guardar_datos()
            self.actualizar_lista_stock()
        except:
            messagebox.showerror("Error", "Valor inválido")

    def eliminar_producto(self, producto):
        if messagebox.askyesno("Confirmar", f"¿Eliminar {producto.nombre}?"):
            self.productos.remove(producto)
            self.guardar_datos()
            self.actualizar_lista_stock()

    def crear_pestana_analisis(self):
        self.tab_analisis = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_analisis, text='Análisis de Margen')
        
        control_frame = ctk.CTkFrame(self.tab_analisis, fg_color="#f0f0f0")
        control_frame.pack(pady=10, padx=10, fill='x')

        self.modo_analisis = ctk.CTkComboBox(control_frame, 
                                           values=['Por Categoría', 'Por Producto'],
                                           command=self.actualizar_analisis,
                                           fg_color="#1e6ba5", button_color="#1e6ba5")
        self.modo_analisis.set('Por Categoría')
        self.modo_analisis.pack(side='left', padx=10)

        self.lbl_margen_promedio = ctk.CTkLabel(control_frame, text="Margen Promedio: 0%", text_color="black")
        self.lbl_margen_promedio.pack(side='left', padx=20)

        self.fig = plt.Figure(figsize=(8, 5), dpi=100, facecolor='white')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#f0f0f0')
        self.canvas_analisis = FigureCanvasTkAgg(self.fig, master=self.tab_analisis)
        self.canvas_analisis.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        self.actualizar_analisis()

    def actualizar_analisis(self, *args):
        self.ax.clear()
        modo = self.modo_analisis.get()
        
        if modo == 'Por Categoría':
            categorias = {p.categoria for p in self.productos}
            margenes = [
                sum(p.margen_ganancia for p in self.productos if p.categoria == cat) / 
                len([p for p in self.productos if p.categoria == cat]) 
                for cat in categorias
            ]
            self.ax.bar(categorias, margenes, color=['#4CAF50' if m >= MARGEN_MINIMO else '#F44336' for m in margenes])
            self.ax.set_title('Margen por Categoría')
        else:
            productos = [p.nombre for p in self.productos]
            margenes = [p.margen_ganancia for p in self.productos]
            self.ax.barh(productos, margenes, color=['#4CAF50' if m >= MARGEN_MINIMO else '#F44336' for m in margenes])
            self.ax.set_title('Margen por Producto')
        
        margen_promedio = sum(p.margen_ganancia for p in self.productos) / len(self.productos) if self.productos else 0
        self.lbl_margen_promedio.configure(text=f"Margen Promedio: {margen_promedio:.1f}%")
        self.canvas_analisis.draw()

    def crear_pestana_historial(self):
        self.tab_historial = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_historial, text='Historial de Ventas')
        
        # Controles de búsqueda
        control_frame = ctk.CTkFrame(self.tab_historial, fg_color="#2b2b2b")
        control_frame.pack(pady=10, padx=10, fill='x')

        ctk.CTkLabel(control_frame, text="Buscar:").pack(side='left', padx=5)
        self.buscar_ventas_entry = ctk.CTkEntry(control_frame, width=200)
        self.buscar_ventas_entry.pack(side='left', padx=5)
        self.buscar_ventas_entry.bind('<KeyRelease>', self.filtrar_historial)

        # Tabla de ventas
        self.tree_ventas = ttk.Treeview(self.tab_historial, columns=('Fecha', 'Producto', 'Cantidad', 'Total'), 
                                      show='headings', style="Custom.Treeview")
        style = ttk.Style()
        style.configure("Custom.Treeview", background="#333333", foreground="white", fieldbackground="#333333")
        style.map("Custom.Treeview", background=[('selected', '#1e6ba5')])
        
        for col in ('Fecha', 'Producto', 'Cantidad', 'Total'):
            self.tree_ventas.heading(col, text=col)
        
        scroll = ttk.Scrollbar(self.tab_historial, orient="vertical", command=self.tree_ventas.yview)
        self.tree_ventas.configure(yscrollcommand=scroll.set)
        
        self.tree_ventas.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')

        # Estadísticas
        stats_frame = ctk.CTkFrame(self.tab_historial, fg_color="#2b2b2b")
        stats_frame.pack(pady=10, padx=10, fill='x')
        
        self.lbl_ventas_totales = ctk.CTkLabel(stats_frame, text="Ventas Totales: $0.00")
        self.lbl_ventas_totales.pack(side='left', padx=20)
        self.lbl_ventas_promedio = ctk.CTkLabel(stats_frame, text="Ticket Promedio: $0.00")
        self.lbl_ventas_promedio.pack(side='left', padx=20)

        self.actualizar_historial()

    def actualizar_historial(self):
        for item in self.tree_ventas.get_children():
            self.tree_ventas.delete(item)
        
        for venta in self.ventas:
            self.tree_ventas.insert('', 'end', values=(
                venta['fecha'], 
                venta['producto'], 
                venta['cantidad'], 
                f"${venta['total']:.2f}"
            ))
        
        total = sum(v['total'] for v in self.ventas)
        promedio = total / len(self.ventas) if self.ventas else 0
        self.lbl_ventas_totales.configure(text=f"Ventas Totales: ${total:.2f}")
        self.lbl_ventas_promedio.configure(text=f"Ticket Promedio: ${promedio:.2f}")

    def filtrar_historial(self, event):
        texto = self.buscar_ventas_entry.get().lower()
        for item in self.tree_ventas.get_children():
            valores = self.tree_ventas.item(item)['values']
            if any(texto in str(v).lower() for v in valores):
                self.tree_ventas.reattach(item, '', 'end')
            else:
                self.tree_ventas.detach(item)

    def crear_pestana_proveedores(self):
        self.tab_proveedores = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.tab_proveedores, text='Proveedores')
        
        main_frame = ctk.CTkFrame(self.tab_proveedores, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Formulario de registro
        registro_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        registro_frame.pack(pady=10, padx=10, fill="x")

        campos = ["Nombre:", "Teléfono:", "Dirección:"]
        self.entries_proveedores = []
        for i, texto in enumerate(campos):
            ctk.CTkLabel(registro_frame, text=texto).grid(row=i, column=0, padx=5, pady=5)
            entry = ctk.CTkEntry(registro_frame, width=250)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries_proveedores.append(entry)

        ctk.CTkButton(registro_frame, text="Registrar Proveedor", 
                    command=self.registrar_proveedor, fg_color="#1e6ba5").grid(row=3, column=0, columnspan=2, pady=10)

        # Lista de proveedores
        lista_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        lista_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.scroll_proveedores = ctk.CTkScrollableFrame(lista_frame, fg_color="#333333")
        self.scroll_proveedores.pack(fill="both", expand=True, padx=5, pady=5)
        self.actualizar_lista_proveedores()

    def registrar_proveedor(self):
        datos = [entry.get().strip() for entry in self.entries_proveedores]
        if not all(datos):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        self.proveedores.append(Proveedor(*datos))
        self.guardar_datos()
        self.actualizar_lista_proveedores()
        for entry in self.entries_proveedores: entry.delete(0, 'end')
        messagebox.showinfo("Éxito", "Proveedor registrado")

    def actualizar_lista_proveedores(self):
        for widget in self.scroll_proveedores.winfo_children():
            widget.destroy()
        
        for proveedor in self.proveedores:
            frame = ctk.CT
