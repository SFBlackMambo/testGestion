DB_HOST = 'localhost'
DB_USER = 'admin'
DB_PASSWORD = 'pass'
DB_DATABASE = 'testSalario'


import tkinter as tk
from tkinter import ttk
import mysql.connector
from mysql.connector import Error

def obtener_empleados():
    """Conecta a la base de datos y obtiene los nombres de los empleados y sus IDs."""
    try:
        conexion = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )
        if conexion.is_connected():
            cursor = conexion.cursor()
            cursor.execute("SELECT id, nombre_empleado, apellido_empleado FROM empleado")
            empleados = cursor.fetchall()
            diccionario_empleados = {f"{nombre} {apellido}": id for id, nombre, apellido in empleados}
            return diccionario_empleados
    except Error as e:
        print(f"Error al conectarse a MySQL: {e}")
    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()

def obtener_semanas_por_empleado(id_empleado):
    """Conecta a la base de datos y obtiene las semanas para el empleado dado."""
    semanas = []
    try:
        conexion = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )
        if conexion.is_connected():
            cursor = conexion.cursor()
            query = """
                SELECT DISTINCT ID_semana
                FROM nomina
                WHERE ID_empleado = %s
                ORDER BY ID_semana;
            """
            cursor.execute(query, (id_empleado,))
            semanas = [row[0] for row in cursor.fetchall()]
    except Error as e:
        print(f"Error al conectarse a MySQL: {e}")
    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()
    return semanas

def mostrar_seleccion(nombre_empleado_seleccionado, diccionario_empleados):
    id_empleado = diccionario_empleados[nombre_empleado_seleccionado]
    semanas = obtener_semanas_por_empleado(id_empleado)

    ventana_detalle = tk.Toplevel()
    ventana_detalle.title("Salario del Empleado")
    ventana_detalle.geometry("300x200")

    tk.Label(ventana_detalle, text=f"Empleado seleccionado:\n{nombre_empleado_seleccionado}", font=("Arial", 12)).pack(pady=20)

    semanas_combobox = ttk.Combobox(ventana_detalle, values=semanas, state="readonly")
    semanas_combobox.set("Selecciona una semana")
    semanas_combobox.pack(pady=10)

    boton_calcular = tk.Button(ventana_detalle, text="Calcular", command=lambda: calcular_salario(id_empleado, semanas_combobox.get()))
    boton_calcular.pack(pady=20)

def obtener_datos_salario(id_empleado, id_semana):
    try:
        conexion = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )
        if conexion.is_connected():
            cursor = conexion.cursor()
            query = """
            SELECT e.nombre_empleado, e.apellido_empleado, p.salario_hora, n.horas_trabajadas, s.fecha_inicio
            FROM empleado e
            JOIN puestos p ON e.ID_puesto = p.ID_puesto
            JOIN nomina n ON e.id = n.ID_empleado
            JOIN semana s ON n.ID_semana = s.ID_semana
            WHERE e.id = %s AND n.ID_semana = %s
            """
            cursor.execute(query, (id_empleado, id_semana))
            result = cursor.fetchone()
            datos_salario = {
                'empleado': f"{result[0]} {result[1]}",
                'inicio_semana': result[4].strftime('%Y-%m-%d'),
                'horas_trabajadas': result[3],
                'pago_por_hora': result[2],
                'total_semana': result[2] * result[3]
            }
            return datos_salario
    except Error as e:
        print(f"Error al conectarse a MySQL: {e}")
    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()
    return {}

def calcular_salario(id_empleado, id_semana):
    datos_salario = obtener_datos_salario(id_empleado, id_semana)

    ventana_salario = tk.Toplevel()
    ventana_salario.title("Detalle del Salario")
    ventana_salario.geometry("700x200")

    columnas = ('empleado', 'inicio_semana', 'horas_trabajadas', 'pago_por_hora', 'total_semana')
    tabla_salario = ttk.Treeview(ventana_salario, columns=columnas, show='headings')

    for col in columnas:
        tabla_salario.heading(col, text=col.replace('_', ' ').title())
        tabla_salario.column(col, width=120)

    tabla_salario.pack(expand=True, fill='both')

    if datos_salario:
        tabla_salario.insert('', tk.END, values=(
            datos_salario['empleado'],
            datos_salario['inicio_semana'],
            datos_salario['horas_trabajadas'],
            f"${datos_salario['pago_por_hora']}",
            f"${datos_salario['total_semana']}"
        ))

def crear_ventana(diccionario_empleados):
    ventana = tk.Tk()
    ventana.title("Calculadora salarial de Empleados")
    ventana.geometry("400x300")

    etiqueta = tk.Label(ventana, text="Selecciona un empleado:", font=("Arial", 12))
    etiqueta.pack(pady=10)

    nombres_empleados = list(diccionario_empleados.keys())
    seleccion_empleado = ttk.Combobox(ventana, values=nombres_empleados, state="readonly")
    seleccion_empleado.pack(pady=5)

    boton = tk.Button(ventana, text="Mostrar Detalle", command=lambda: mostrar_seleccion(seleccion_empleado.get(), diccionario_empleados))
    boton.pack(pady=20)

    ventana.mainloop()

if __name__ == "__main__":
    diccionario_empleados = obtener_empleados()
    if diccionario_empleados:
        crear_ventana(diccionario_empleados)
    else:
        print("No se pudieron obtener los empleados.")
