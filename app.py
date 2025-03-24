from flask import Flask, request, jsonify
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import qrcode
import os

app = Flask(__name__)

# Configuración de SMTP (para Gmail)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
GMAIL_USER = os.environ.get('EMAIL_USER')
GMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

# Función para enviar el correo
def enviar_correo(destinatario, mensaje):
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = destinatario
        msg['Subject'] = 'Código QR para retiro de producto'
        
        msg.attach(MIMEText(mensaje, 'plain'))
        
        server.sendmail(GMAIL_USER, destinatario, msg.as_string())
        server.quit()
        print(f"Correo enviado a {destinatario}")
    except Exception as e:
        print(f"Error al enviar el correo: {str(e)}")

# Ruta para generar y enviar el código QR
@app.route('/generar_qr', methods=['POST'])
def generar_qr():
    data = request.get_json()
    email = data.get('email')
    producto = data.get('producto')

    if not email or not producto:
        return jsonify({"error": "Faltan parámetros en la solicitud"}), 400

    # Generar el código QR
    qr_data = f"Producto: {producto}\nCorreo: {email}"
    qr = qrcode.make(qr_data)
    qr_file = f"static/{producto}.png"
    qr.save(qr_file)

    # Enviar el correo con el QR
    mensaje = f"Has seleccionado el producto: {producto}. Tu código QR está adjunto."
    enviar_correo(email, mensaje)

    return jsonify({
        'expiracion': 3379773973.526267,  # Establecer el valor de expiración
        'pedido_id': f"PEDIDO-{producto}",
        'qr_url': qr_file
    })

if __name__ == '__main__':
    app.run(debug=True)
