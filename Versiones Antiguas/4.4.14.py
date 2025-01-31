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
