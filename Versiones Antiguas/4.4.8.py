# gestion_stock.py
import json
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, ttk
import logging
import hashlib

# Configuración inicial
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GestionStock:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Stock")
        self.root.withdraw()
        
        # Maximizar ventana principal (compatible con Linux/Windows)
        self.root.attributes('-zoomed', True)  # <--- Cambio clave aquí
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # ... (resto de inicializaciones)
        self.mostrar_login()

    def centrar_ventana(self, ventana, ancho=400, alto=300):
        """Centra una ventana en la pantalla"""
        pantalla_ancho = ventana.winfo_screenwidth()
        pantalla_alto = ventana.winfo_screenheight()
        x = (pantalla_ancho - ancho) // 2
        y = (pantalla_alto - alto) // 2
        ventana.geometry(f'{ancho}x{alto}+{x}+{y}')

    def mostrar_login(self):
        self.login_window = ctk.CTkToplevel(self.root)
        self.login_window.title("Inicio de Sesión")
        self.centrar_ventana(self.login_window)
        
        # Configuración CORREGIDA de widgets
        campos = [
            ("Usuario:", ctk.CTkEntry(self.login_window)),
            ("Contraseña:", ctk.CTkEntry(self.login_window, show="*")),
            ("Rol:", ctk.CTkComboBox(
                self.login_window,
                values=["admin", "normal"],
                state="readonly"
            ))
        ]
        
        for label, widget in campos:
            ctk.CTkLabel(self.login_window, text=label).pack(pady=5)
            widget.pack(pady=5)
            if label == "Rol:":
                widget.set("normal")

        # Botones CORREGIDOS
        btn_frame = ctk.CTkFrame(self.login_window)
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, 
                    text="Iniciar Sesión", 
                    command=self.iniciar_sesion).pack(side="left", padx=10)
        
        ctk.CTkButton(btn_frame,
                    text="Registrarse",
                    command=self.registrar_usuario).pack(side="left", padx=10)

    def iniciar_sesion(self):
        # ... (implementación de login)
        self.root.deiconify()  # Mostrar ventana principal maximizada

if __name__ == "__main__":
    root = ctk.CTk()
    app = GestionStock(root)
    root.mainloop()
