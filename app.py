from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)

# Configuración de SMTP (para Gmail)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
GMAIL_USER = os.environ.get('EMAIL_USER')  # Tu correo de Gmail (en variable de entorno)
GMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')  # Tu contraseña de Gmail o contraseña de aplicación

@app.route('/generar_qr', methods=['POST'])
def generar_qr():
    # Obtener los datos de la solicitud JSON
    data = request.get_json()

    if 'email' not in data or 'producto' not in data:
        return jsonify({'error': 'Faltan parámetros en la solicitud'}), 400

    email = data['email']
    producto = data['producto']
    
    print(f"Datos recibidos - Email: {email}, Producto: {producto}")  # Verifica los datos

    # Generar el QR (esto es solo un ejemplo)
    qr_url = f"static/{producto}.png"  # Aquí deberías generar realmente el QR, esto es solo un ejemplo
    print(f"QR generado: {qr_url}")

    # Enviar el correo con el QR (esto es un ejemplo de cómo enviarlo)
    try:
        # Crear el mensaje de correo
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = email
        msg['Subject'] = 'Tu Código QR para el Producto'

        # Cuerpo del correo
        body = f"Hola! Aquí tienes tu código QR para el producto {producto}: {qr_url}"
        msg.attach(MIMEText(body, 'plain'))

        # Configurar el servidor SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Usar seguridad TLS
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        
        # Enviar el correo
        server.sendmail(GMAIL_USER, email, msg.as_string())
        server.quit()
        
        print(f"Correo enviado a {email} exitosamente.")

        return jsonify({
            'expiracion': 3379773973.526267,
            'pedido_id': f'PEDIDO-{producto}',
            'qr_url': qr_url
        })

    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return jsonify({'error': 'Error al enviar el correo'}), 500

if __name__ == '__main__':
    app.run(debug=True)
