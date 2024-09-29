#!/usr/bin/env python

import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import mysql.connector
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Función para conectar a la base de datos
def connect_db():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWD'),
        database=os.getenv('DB_DB'),
        charset='utf8mb4',
        collation='utf8mb4_general_ci'
    )

class ReservationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin - Gestión de Reservas")

        # Crear el contenedor de filtros
        self.filter_frame = tk.Frame(root)
        self.filter_frame.pack(fill=tk.X)

        # Crear la tabla
        self.tree = ttk.Treeview(root, columns=("ID", "Nombre", "Evento", "Email", "Espacio", "Fecha", "Hora Inicio", "Montaje", "Depto", "Hora Fin", "Estado", "Espacio Asignado"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Evento", text="Evento")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Espacio", text="Espacio")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Hora Inicio", text="Hora Inicio")
        self.tree.heading("Montaje", text="Montaje")
        self.tree.heading("Depto", text="Depto")
        self.tree.heading("Hora Fin", text="Hora Fin")
        self.tree.heading("Estado", text="Estado")
        self.tree.heading("Espacio Asignado", text="Espacio Asignado")
        
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Botones
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X)

        self.refresh_btn = tk.Button(btn_frame, text="Refrescar", command=self.load_data)
        self.refresh_btn.pack(side=tk.LEFT)
        
        self.edit_btn = tk.Button(btn_frame, text="Editar", command=self.edit_reservation)
        self.edit_btn.pack(side=tk.LEFT)
        
        self.delete_btn = tk.Button(btn_frame, text="Eliminar", command=self.delete_reservation)
        self.delete_btn.pack(side=tk.LEFT)
        
        self.cancel_btn = tk.Button(btn_frame, text="Cancelar", command=self.cancel_reservation)
        self.cancel_btn.pack(side=tk.LEFT)
        
        self.filters = {}
        self.create_filters()
        self.load_data()

    def create_filters(self):
        # Crear filtros para ID, Nombre, Email y Fecha
        filter_fields = ["ID", "Nombre", "Email", "Fecha"]
        for col in filter_fields:
            label = tk.Label(self.filter_frame, text=col)
            label.pack(side=tk.LEFT, padx=5, pady=5)
            if col == "Fecha":
                entry = DateEntry(self.filter_frame, date_pattern='yyyy-mm-dd')
            else:
                entry = ttk.Combobox(self.filter_frame)
            entry.pack(side=tk.LEFT, padx=5, pady=5)
            entry.bind("<<ComboboxSelected>>" if col != "Fecha" else "<FocusOut>", self.apply_filters)
            self.filters[col] = entry

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reservas")
        rows = cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)
        
        cursor.close()
        conn.close()

        self.adjust_column_widths(rows)
        self.update_filters()

    def adjust_column_widths(self, rows):
        # Ajustar los anchos de las columnas basándose en los datos
        for col in self.tree["columns"]:
            max_width = max(len(str(item)) for item in [col] + [row[self.tree["columns"].index(col)] for row in rows]) * 10
            self.tree.column(col, width=max_width)

    def update_filters(self):
        # Actualizar los valores de los filtros basándose en los datos cargados
        for col in self.filters.keys():
            if col != "Fecha":
                values = set()
                col_index = self.tree["columns"].index(col)
                for row in self.tree.get_children():
                    item = self.tree.item(row)
                    value = item["values"][col_index]
                    values.add(value.lower() if isinstance(value, str) else value)
                self.filters[col]["values"] = list(values)

    def apply_filters(self, event=None):
        # Aplicar los filtros seleccionados
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = connect_db()
        cursor = conn.cursor()
        query = "SELECT * FROM reservas WHERE 1=1"
        params = []
        for col in self.filters.keys():
            value = self.filters[col].get()
            if value:
                if col == "Fecha":
                    query += " AND DATE(fecha) = %s"
                else:
                    query += f" AND LOWER({col.lower()}) = %s"
                params.append(value.lower() if col != "Fecha" else value)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)
        
        cursor.close()
        conn.close()

    def edit_reservation(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor selecciona una reserva para editar.")
            return
        
        item = self.tree.item(selected_item)
        values = item["values"]
        
        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("Editar Reserva")
        
        # Crear entradas para cada campo
        fields = [
            ("Nombre", values[1]),
            ("Evento", values[2]),
            ("Email", values[3]),
            ("Espacio", values[4]),
            ("Fecha", values[5]),
            ("Hora Inicio", values[6]),
            ("Hora Fin", values[7]),
            ("Montaje", values[8]),
            ("Depto", values[9]),
            ("Estado", values[10]),
            ("Espacio Asignado", values[11])
        ]
        
        self.entries = {}
        for idx, (label, value) in enumerate(fields):
            tk.Label(self.edit_window, text=f"{label}:").grid(row=idx, column=0, sticky=tk.W, padx=10, pady=5)
            entry = tk.Entry(self.edit_window)
            entry.insert(0, value)
            entry.grid(row=idx, column=1, sticky=tk.EW, padx=10, pady=5)
            self.entries[label] = entry
        
        self.edit_window.grid_columnconfigure(1, weight=1)  # Make column 1 expand
        self.edit_window.grid_rowconfigure(len(fields), weight=1)  # Make row for buttons expand
        
        self.save_btn = tk.Button(self.edit_window, text="Guardar", command=lambda: self.save_changes(values[0]))
        self.save_btn.grid(row=len(fields), column=0, columnspan=2, pady=10)
    
    def save_changes(self, reservation_id):
        # Obtener valores
        assigned_space = self.entries["Espacio Asignado"].get()
        if assigned_space == "":
            assigned_space = None

        # Asegurar que hora_inicio y hora_fin son válidos o les asignar un valor predeterminado
        start_time = self.entries["Hora Inicio"].get()
        end_time = self.entries["Hora Fin"].get()
        
        if start_time == "":
            start_time = None
        if end_time == "":
            end_time = None
        
        # Guardar cambios
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE reservas 
            SET nombre=%s, nombre_evento=%s, email=%s, espacio=%s, fecha=%s, hora_inicio=%s, montaje_especial=%s, departamento=%s, hora_fin=%s, estado=%s, espacio_asignado=%s 
            WHERE id=%s
        """, (
            self.entries["Nombre"].get(), self.entries["Evento"].get(), self.entries["Email"].get(), self.entries["Espacio"].get(), 
            self.entries["Fecha"].get(), start_time, end_time, 
            self.entries["Montaje"].get(), self.entries["Depto"].get(), self.entries["Estado"].get(), 
            assigned_space, reservation_id
        ))
        conn.commit()
        cursor.close()
        conn.close()
        
        self.edit_window.destroy()
        self.load_data()
    
    def delete_reservation(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor selecciona una reserva para eliminar.")
            return
        
        item = self.tree.item(selected_item)
        reservation_id = item["values"][0]
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reservas WHERE id=%s", (reservation_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        self.load_data()
    
    def cancel_reservation(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor selecciona una reserva para cancelar.")
            return
        
        item = self.tree.item(selected_item)
        reservation_id = item["values"][0]
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE reservas SET estado='cancelada' WHERE id=%s", (reservation_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        self.load_data()

if __name__ == "__main__":
    root = tk.Tk()
    app = ReservationApp(root)
    root.mainloop()
