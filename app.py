from flask import Flask, jsonify, request
import qrcode
import os
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

app = Flask(__name__)

# Configuración de SMTP (para Gmail)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
GMAIL_USER = 'tu_correo@gmail.com'  # Tu correo de Gmail
GMAIL_PASSWORD = 'tu_contraseña'  # Tu contraseña de Gmail o contraseña de aplicación

def enviar_correo(destinatario, subject, body, image_path):
    try:
        # Crear el mensaje
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = destinatario
        msg['Subject'] = subject

        # Cuerpo del mensaje
        msg.attach(MIMEText(body, 'plain'))

        # Adjuntar el archivo de imagen
        with open(image_path, 'rb') as file:
            img = MIMEImage(file.read())
            img.add_header('Content-ID', '<qr_image>')
            msg.attach(img)

        # Conectar al servidor SMTP y enviar el correo
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Establecer la conexión segura
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, destinatario, msg.as_string())
        server.quit()
        print("Correo enviado exitosamente")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

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
        email_destinatario = data['email']

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

        # Enviar el correo con el código QR adjunto
        subject = f"Tu código QR para el pedido {pedido_id}"
        body = f"Hola, aquí está tu código QR para el pedido {pedido_id}. Caducará a las {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expiration_time))}."
        enviar_correo(email_destinatario, subject, body, img_path)

        # Devolver la respuesta con el enlace al QR y la expiración
        return jsonify({
            'pedido_id': pedido_id,
            'expiracion': expiration_time,
            'qr_url': img_path
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
