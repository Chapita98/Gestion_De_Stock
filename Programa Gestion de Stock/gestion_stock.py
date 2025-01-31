import json
import hashlib
import customtkinter as ctk
from tkinter import messagebox

ARCHIVO_USUARIOS = "usuarios.json"

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
        self.root.withdraw()  # Ocultar ventana principal
        
        self.usuarios = []
        self.current_user = None
        
        self.cargar_usuarios()
        self.mostrar_login()
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

    def centrar_ventana(self, ventana, ancho=400, alto=300):
        """Centra una ventana en la pantalla"""
        ventana.update_idletasks()
        pantalla_ancho = ventana.winfo_screenwidth()
        pantalla_alto = ventana.winfo_screenheight()
        x = (pantalla_ancho - ancho) // 2
        y = (pantalla_alto - alto) // 2
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

    def cargar_usuarios(self):
        try:
            with open(ARCHIVO_USUARIOS, "r") as file:
                self.usuarios = [Usuario(**user) for user in json.load(file)]
        except FileNotFoundError:
            # Crear usuarios predeterminados
            self.usuarios = [
                Usuario("super", "admin123", "clave_super", "super"),
                Usuario("admin", "admin123", "clave_admin", "admin"),
                Usuario("usuario", "user123", "clave_usuario", "normal")
            ]
            self.guardar_usuarios()

    def guardar_usuarios(self):
        with open(ARCHIVO_USUARIOS, "w") as file:
            json.dump([vars(u) for u in self.usuarios], file, indent=4)

    def mostrar_login(self):
        """Muestra la ventana de login centrada"""
        self.login_window = ctk.CTkToplevel(self.root)
        self.login_window.title("Inicio de Sesión")
        self.centrar_ventana(self.login_window, 400, 350)
        self.login_window.grab_set()  # Bloquear otras ventanas
        
        # Contenido del login
        frame = ctk.CTkFrame(self.login_window)
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        usuarios_normales = [u.usuario for u in self.usuarios if u.usuario != "super"]
        
        ctk.CTkLabel(frame, text="Seleccione usuario:").pack(pady=10)
        self.cmb_usuarios = ctk.CTkComboBox(frame, values=usuarios_normales)
        self.cmb_usuarios.pack(pady=5, fill="x")
        
        ctk.CTkLabel(frame, text="Contraseña:").pack(pady=5)
        self.entry_pass = ctk.CTkEntry(frame, show="*")
        self.entry_pass.pack(pady=5, fill="x")
        
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(pady=15, fill="x")
        
        ctk.CTkButton(btn_frame, text="Ingresar", command=self.validar_login_normal).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Superusuario", command=self.mostrar_login_super).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Salir", command=self.root.destroy).pack(side="right", padx=5)

    def mostrar_login_super(self):
        """Ventana de login para superusuario"""
        super_window = ctk.CTkToplevel(self.login_window)
        super_window.title("Acceso Superusuario")
        self.centrar_ventana(super_window, 300, 200)
        super_window.grab_set()
        
        frame = ctk.CTkFrame(super_window)
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        ctk.CTkLabel(frame, text="Usuario:").pack(pady=5)
        self.entry_super_user = ctk.CTkEntry(frame)
        self.entry_super_user.pack(pady=5, fill="x")
        
        ctk.CTkLabel(frame, text="Contraseña:").pack(pady=5)
        self.entry_super_pass = ctk.CTkEntry(frame, show="*")
        self.entry_super_pass.pack(pady=5, fill="x")
        
        ctk.CTkButton(frame, text="Ingresar", command=self.validar_login_super).pack(pady=10)

    def validar_login_normal(self):
        usuario = self.cmb_usuarios.get()
        password = self.entry_pass.get()
        
        if usuario and password:
            user = next((u for u in self.usuarios 
                        if u.usuario == usuario 
                        and u.contrasena == Usuario._hash_contrasena(password)), None)
            if user:
                self.current_user = user
                self.login_window.destroy()
                self.mostrar_interfaz_principal()
                return
        messagebox.showerror("Error", "Credenciales inválidas", parent=self.login_window)

    def validar_login_super(self):
        usuario = self.entry_super_user.get()
        password = self.entry_super_pass.get()
        
        if usuario == "super" and password == "admin123":
            user = next((u for u in self.usuarios if u.usuario == "super"), None)
            if user:
                self.current_user = user
                self.login_window.destroy()
                self.mostrar_interfaz_principal()
                return
        messagebox.showerror("Error", "Credenciales incorrectas", parent=self.entry_super_user.winfo_toplevel())

    def mostrar_interfaz_principal(self):
        """Muestra la interfaz principal centrada"""
        self.root.deiconify()  # Mostrar ventana principal
        self.centrar_ventana(self.root, 1200, 800)  # Tamaño para pantalla completa
        
        # Barra de herramientas
        toolbar = ctk.CTkFrame(self.root)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(toolbar, text=f"Usuario: {self.current_user.usuario} ({self.current_user.rol})").pack(side="left")
        ctk.CTkButton(toolbar, text="Cerrar Sesión", command=self.cerrar_sesion).pack(side="right")

    def cerrar_sesion(self):
        """Vuelve a la pantalla de login"""
        self.root.withdraw()
        self.mostrar_login()

if __name__ == "__main__":
    root = ctk.CTk()
    app = GestionStock(root)
    root.mainloop()
