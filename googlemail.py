import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from my_secrets.notion_secrets import SMTP_USERNAME
from my_secrets.notion_secrets import SMTP_PWD

def send_email(to_address, subject, body, attachment_path):
    # Paramètres SMTP Gmail
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # Destinataire et expéditeur
    from_address = SMTP_USERNAME
    to_address = to_address

    # Création du message
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    # Corps du message
    msg.attach(MIMEText(body, 'plain'))

    if attachment_path != '' : 
    # Pièce jointe
        with open(attachment_path, 'rb') as attachment:
            part = MIMEApplication(attachment.read())
            part.add_header('Content-Disposition', 'attachment', filename=attachment_path)
            msg.attach(part)

        # Connexion au serveur SMTP et envoi de l'e-mail
    with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PWD)
            server.sendmail(from_address, to_address, msg.as_string())

