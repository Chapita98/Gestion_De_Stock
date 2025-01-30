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
        
        self._maximizar_ventana()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.usuarios = []
        self.current_user = None
        
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
        except:
            self.root.geometry("1200x800")

    def cargar_datos(self):
        try:
            with open(ARCHIVO_USUARIOS, "r") as file:
                usuarios_data = json.load(file)
                self.usuarios = [Usuario(**user) for user in usuarios_data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.usuarios = []

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
        
        campos = [
            ("Usuario:", ctk.CTkEntry(self.login_window)),
            ("Contraseña:", ctk.CTkEntry(self.login_window, show="*")),
            ("Rol:", ctk.CTkComboBox(self.login_window, values=["admin", "normal"], state="readonly"))
        ]
        
        self.entries = []
        for label, widget in campos:
            ctk.CTkLabel(self.login_window, text=label).pack(pady=5)
            widget.pack(pady=5)
            self.entries.append(widget)
        
        self.entries[2].set("normal")

        btn_frame = ctk.CTkFrame(self.login_window)
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Iniciar Sesión", command=self.iniciar_sesion).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Registrarse", command=self.registrar_usuario).pack(side="left", padx=10)

    def iniciar_sesion(self):
        usuario = self.entries[0].get()
        contrasena = self.entries[1].get()
        rol = self.entries[2].get()

        if not all([usuario, contrasena]):
            messagebox.showerror("Error", "Complete todos los campos")
            return

        user = next((u for u in self.usuarios 
                    if u.usuario == usuario 
                    and u.contrasena == Usuario._hash_contrasena(contrasena)
                    and u.rol == rol), None)
        
        if user:
            self.current_user = user
            self.login_window.destroy()
            self.root.deiconify()
        else:
            messagebox.showerror("Error", "Credenciales inválidas")

    def registrar_usuario(self):
        usuario = self.entries[0].get()
        contrasena = self.entries[1].get()
        rol = self.entries[2].get()

        if any(u.usuario == usuario for u in self.usuarios):
            messagebox.showerror("Error", "Usuario ya existe")
            return

        if not all([usuario, contrasena]):
            messagebox.showerror("Error", "Complete todos los campos")
            return

        nuevo_usuario = Usuario(usuario, contrasena, "clave_temp", rol)
        self.usuarios.append(nuevo_usuario)
        self.guardar_datos()
        messagebox.showinfo("Éxito", "Usuario registrado correctamente")

    def cerrar_aplicacion(self):
        self.guardar_datos()
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = GestionStock(root)
    root.mainloop()
