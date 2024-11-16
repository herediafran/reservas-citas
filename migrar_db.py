import sqlite3

DB_FILE = "reservas.db"

def migrar_base_datos():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Verifica si la columna 'apellidos' ya existe
    cursor.execute("PRAGMA table_info(reservas)")
    columnas = [col[1] for col in cursor.fetchall()]

    if "apellidos" not in columnas:
        # Crea una nueva tabla con la columna 'apellidos'
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservas_nueva (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                hora TEXT NOT NULL,
                nombre TEXT NOT NULL,
                apellidos TEXT NOT NULL
            )
        """)

        # Copia los datos de la tabla antigua a la nueva, usando valores vacíos para 'apellidos'
        cursor.execute("""
            INSERT INTO reservas_nueva (id, fecha, hora, nombre, apellidos)
            SELECT id, fecha, hora, nombre, '' AS apellidos FROM reservas
        """)

        # Renombra las tablas
        cursor.execute("DROP TABLE reservas")
        cursor.execute("ALTER TABLE reservas_nueva RENAME TO reservas")
        print("Migración completada con éxito.")

    else:
        print("La tabla ya tiene la columna 'apellidos'. No se requiere migración.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrar_base_datos()
