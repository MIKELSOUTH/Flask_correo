from flask import Flask, jsonify, request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import qrcode
import os
import time

# Configuración de SMTP (para Gmail)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
GMAIL_USER = os.environ.get('EMAIL_USER')  # Tu correo de Gmail (en variable de entorno)
GMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')  # Tu contraseña de Gmail o contraseña de aplicación

app = Flask(__name__)

@app.route('/')
def index():
    return "Servidor Flask en funcionamiento"

@app.route('/generar_qr', methods=['POST'])
def generar_qr():
    try:
        # Obtener los datos del cuerpo de la solicitud
        data = request.get_json()

        # Verificar que los datos necesarios estén presentes
        if 'pedido_id' not in data or 'expiracion' not in data or 'email' not in data:
            return jsonify({'error': 'Faltan parámetros en la solicitud'}), 400

        pedido_id = data['pedido_id']
        expiracion = data['expiracion']
        email_cliente = data['email']

        # Crear el contenido del QR
        qr_content = f"{pedido_id},{expiracion}"

        # Generar el código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)

        # Crear la imagen del QR
        img = qr.make_image(fill='black', back_color='white')

        # Crear un nombre único para el archivo QR
        qr_filename = f"{pedido_id}.png"

        # Guardar el archivo en la carpeta 'static'
        img_path = os.path.join('static', qr_filename)
        img.save(img_path)

        # Calcular la fecha de expiración en formato UNIX (timestamp)
        expiration_time = time.time() + expiracion

        # Enviar el QR por correo
        send_email(email_cliente, qr_filename)

        # Devolver la respuesta con el enlace al QR y la expiración
        return jsonify({
            'pedido_id': pedido_id,
            'expiracion': expiration_time,
            'qr_url': img_path
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def send_email(email_cliente, qr_filename):
    try:
        # Crear el objeto de mensaje
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = email_cliente
        msg['Subject'] = 'Tu código QR para el pedido'

        # Cuerpo del mensaje
        body = 'Adjunto encontrarás el código QR para retirar tu producto.'
        msg.attach(MIMEText(body, 'plain'))

        # Adjuntar el archivo QR
        with open(os.path.join('static', qr_filename), 'rb') as attachment:
            part = MIMEText(attachment.read(), 'base64', 'utf-8')
            part.add_header('Content-Disposition', 'attachment', filename=qr_filename)
            msg.attach(part)

        # Conexión al servidor SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Usar TLS
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(GMAIL_USER, email_cliente, text)

    except Exception as e:
        print(f"Error al enviar correo: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
