import tkinter as tk
from tkinter import ttk, messagebox
from api_client import listar_herramientas

def cargar_herramientas():
    try:
        herramientas = listar_herramientas()
        tabla.delete(*tabla.get_children())  # Limpiar tabla
        for h in herramientas:
            tabla.insert("", "end", values=(
                h["id"], h["nombre"], h["estado"], h["categoria"]["nombre"]
            ))
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar: {e}")

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Inventario de Herramientas")
ventana.geometry("700x400")

# Botón para actualizar
btn_actualizar = ttk.Button(ventana, text="Cargar Herramientas", command=cargar_herramientas)
btn_actualizar.pack(pady=10)

# Tabla de herramientas
columnas = ("ID", "Nombre", "Estado", "Categoría")
tabla = ttk.Treeview(ventana, columns=columnas, show="headings")

for col in columnas:
    tabla.heading(col, text=col)
    tabla.column(col, width=150)

tabla.pack(expand=True, fill="both", padx=10, pady=10)

ventana.mainloop()
