from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Configuración de la base de datos
DB_FILE = "reservas.db"

# Configuración del servidor de correo
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "herediafran2000@gmail.com"
EMAIL_PASSWORD = "fnpi xcwv mayh giai"
TRABAJADOR_EMAIL = "herediafran2000@gmail.com"

HORAS_DISPONIBLES = [f"{hour}:00" for hour in range(10, 21)]


def init_db():
    """Inicializa la base de datos con una tabla de reservas."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            nombre TEXT NOT NULL,
            apellidos TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def obtener_fechas_disponibles():
    """Genera las fechas disponibles desde hoy hasta una semana adelante, excluyendo sábados y domingos."""
    hoy = datetime.now()
    fechas = []
    for i in range(8):
        dia = hoy + timedelta(days=i)
        if dia.weekday() < 5:  # 0=Lunes, 4=Viernes
            fechas.append(dia.strftime("%Y-%m-%d"))
    return fechas


def obtener_reservas():
    """Obtiene las reservas de la base de datos."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT fecha, hora, nombre, apellidos FROM reservas")
    reservas = cursor.fetchall()
    conn.close()
    reservas_por_fecha = {fecha: {hora: None for hora in HORAS_DISPONIBLES} for fecha in obtener_fechas_disponibles()}
    for fecha, hora, nombre, apellidos in reservas:
        if fecha in reservas_por_fecha:
            reservas_por_fecha[fecha][hora] = f"{nombre} {apellidos}"
    return reservas_por_fecha


def enviar_correo(fecha, hora, nombre, apellidos):
    """Envía un correo al trabajador con los detalles de la reserva."""
    try:
        mensaje = MIMEMultipart()
        mensaje["From"] = EMAIL_USER
        mensaje["To"] = TRABAJADOR_EMAIL
        mensaje["Subject"] = "Nueva Reserva de Cita"
        cuerpo = f"Hola,\n\nSe ha realizado una nueva reserva:\n- Nombre: {nombre} {apellidos}\n- Fecha: {fecha}\n- Hora: {hora}\n\nSaludos,\nSistema de Reservas"
        mensaje.attach(MIMEText(cuerpo, "plain"))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as servidor:
            servidor.starttls()
            servidor.login(EMAIL_USER, EMAIL_PASSWORD)
            servidor.sendmail(EMAIL_USER, TRABAJADOR_EMAIL, mensaje.as_string())
        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")


@app.route("/")
def index():
    fechas_disponibles = obtener_fechas_disponibles()
    reservas = obtener_reservas()
    return render_template("index.html", fechas=fechas_disponibles, horas=HORAS_DISPONIBLES, reservas=reservas)


@app.route("/api/reservar", methods=["POST"])
def reservar():
    data = request.json
    fecha = data.get("fecha")
    hora = data.get("hora")
    nombre = data.get("nombre")
    apellidos = data.get("apellidos")

    if not fecha or not hora or not nombre or not apellidos:
        return jsonify({"message": "Todos los campos son obligatorios"}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reservas WHERE fecha = ? AND hora = ?", (fecha, hora))
    reserva = cursor.fetchone()
    if reserva:
        conn.close()
        return jsonify({"message": "La fecha u hora ya están reservadas"}), 400

    cursor.execute("INSERT INTO reservas (fecha, hora, nombre, apellidos) VALUES (?, ?, ?, ?)", (fecha, hora, nombre, apellidos))
    conn.commit()
    conn.close()
    enviar_correo(fecha, hora, nombre, apellidos)
    return jsonify({"message": f"Reserva para {fecha} a las {hora} confirmada"}), 200


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
