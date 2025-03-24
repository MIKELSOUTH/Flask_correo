from flask import Flask, jsonify, request
import qrcode
import os
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from flask_cors import CORS #Importamos CORS

app = Flask(__name__)
CORS(app) #Habilitamos CORS

# Configuración de SMTP (para Gmail)
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = os.environ.get('SMTP_PORT', 587)
GMAIL_USER = os.environ.get('EMAIL_USER')
GMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

# Función para enviar correo electrónico
def send_email(recipient_email, qr_image_path, pedido_id):
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = recipient_email
        msg['Subject'] = f"Tu código QR para el pedido {pedido_id}"

        body = MIMEText(f"Hola,\n\nAquí tienes el código QR para tu pedido {pedido_id}. El código QR es válido hasta la expiración indicada.", 'plain')
        msg.attach(body)

        with open(qr_image_path, 'rb') as qr_file:
            qr_image = MIMEImage(qr_file.read())
            qr_image.add_header('Content-Disposition', 'attachment', filename=os.path.basename(qr_image_path))
            msg.attach(qr_image)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, recipient_email, msg.as_string())

        print(f"Correo enviado a {recipient_email} con el código QR.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

@app.route('/')
def index():
    return "Servidor Flask en funcionamiento"

@app.route('/generar_qr', methods=['POST'])
def generar_qr():
    try:
        data = request.get_json()
        print("Datos recibidos:", data) #Agregamos registro de depuración
        print(f"correo {GMAIL_USER}") #Agregamos registro de depuración
        print(f"contraseña {GMAIL_PASSWORD}") #Agregamos registro de depuración

        if 'pedido_id' not in data or 'expiracion' not in data or 'email' not in data:
            return jsonify({'error': 'Faltan parámetros en la solicitud'}), 400

        pedido_id = data['pedido_id']
        expiracion = data['expiracion']
        email_cliente = data['email']

        qr_content = f"{pedido_id},{expiracion}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)

        qr_filename = f"{pedido_id}.png"
        img_path = os.path.join('static', qr_filename)
        img.save(img_path)

        expiration_time = time.time() + expiracion

        send_email(email_cliente, img_path, pedido_id)

        return jsonify({
            'pedido_id': pedido_id,
            'expiracion': expiration_time,
            'qr_url': img_path
        })

    except Exception as e:
        print("Error:", e) #Agregamos registro de depuración
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
