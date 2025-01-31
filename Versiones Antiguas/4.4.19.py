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
        self.usuarios = []
        self.current_user = None
        
        self.cargar_usuarios()
        self.mostrar_login()
        
    def cargar_usuarios(self):
        try:
            with open(ARCHIVO_USUARIOS, "r") as file:
                self.usuarios = [Usuario(**user) for user in json.load(file)]
        except FileNotFoundError:
            messagebox.showerror("Error", "Archivo de usuarios no encontrado")

    def mostrar_login(self):
        self.login_window = ctk.CTkToplevel(self.root)
        self.login_window.title("Inicio de Sesión")
        
        # Frame principal
        frame = ctk.CTkFrame(self.login_window)
        frame.pack(padx=20, pady=20)
        
        # Lista de usuarios (excluyendo superusuario)
        usuarios_normales = [u.usuario for u in self.usuarios if u.rol != "super"]
        
        ctk.CTkLabel(frame, text="Seleccione usuario:").grid(row=0, column=0, pady=10)
        self.cmb_usuarios = ctk.CTkComboBox(frame, values=usuarios_normales)
        self.cmb_usuarios.grid(row=1, column=0, pady=5)
        
        ctk.CTkLabel(frame, text="Contraseña:").grid(row=2, column=0, pady=5)
        self.entry_pass = ctk.CTkEntry(frame, show="*")
        self.entry_pass.grid(row=3, column=0, pady=5)
        
        # Botones
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.grid(row=4, column=0, pady=15)
        
        ctk.CTkButton(btn_frame, text="Ingresar", command=self.validar_login_normal).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Superusuario", command=self.mostrar_login_super).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Salir", command=self.root.destroy).pack(side="right", padx=5)

    def mostrar_login_super(self):
        super_window = ctk.CTkToplevel(self.login_window)
        super_window.title("Login Superusuario")
        
        frame = ctk.CTkFrame(super_window)
        frame.pack(padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="Usuario:").grid(row=0, column=0, pady=5)
        self.entry_super_user = ctk.CTkEntry(frame)
        self.entry_super_user.grid(row=1, column=0, pady=5)
        
        ctk.CTkLabel(frame, text="Contraseña:").grid(row=2, column=0, pady=5)
        self.entry_super_pass = ctk.CTkEntry(frame, show="*")
        self.entry_super_pass.grid(row=3, column=0, pady=5)
        
        ctk.CTkButton(frame, text="Ingresar", command=self.validar_login_super).grid(row=4, column=0, pady=10)

    def validar_login_normal(self):
        usuario = self.cmb_usuarios.get()
        password = self.entry_pass.get()
        
        user = next((u for u in self.usuarios 
                    if u.usuario == usuario 
                    and u.contrasena == Usuario._hash_contrasena(password)), None)
        
        if user:
            self.current_user = user
            self.login_window.destroy()
            self.mostrar_interfaz()
        else:
            messagebox.showerror("Error", "Credenciales inválidas")

    def validar_login_super(self):
        usuario = self.entry_super_user.get()
        password = self.entry_super_pass.get()
        
        if usuario == "super" and password == "admin123":
            user = next((u for u in self.usuarios if u.usuario == "super"), None)
            if user:
                self.current_user = user
                self.login_window.destroy()
                self.mostrar_interfaz()
                return
        
        messagebox.showerror("Error", "Credenciales de superusuario inválidas")

    def mostrar_interfaz(self):
        self.root.deiconify()
        toolbar = ctk.CTkFrame(self.root)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(toolbar, 
                    text=f"Usuario: {self.current_user.usuario} ({self.current_user.rol})").pack(side="left")
        
        ctk.CTkButton(toolbar, 
                     text="Cerrar Sesión", 
                     command=self.cerrar_sesion).pack(side="right")

    def cerrar_sesion(self):
        self.root.withdraw()
        self.mostrar_login()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = GestionStock(root)
    root.mainloop()
