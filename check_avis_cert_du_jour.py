# --------------------------------------------------------------------------
# Vérifie les AVIS du CERTFR publié la veille (https://www.cert.ssi.gouv.fr/avis/)
#  - récupére les infos pour chaque AVIS
#  - envoie un mail avec les infos clés de chaque AVIS
# Vérifie les Alertes du CERTFR publiées la veille (https://www.cert.ssi.gouv.fr/alerte/)
#  - récupére les infos pour chaque Alerte
#  - envoie un mail avec les infos clés de chaque Alerte
# --------------------------------------------------------------------------
import feedparser
import subprocess
from datetime import datetime, timezone, timedelta
import win32com.client as win32
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def recuperer_flux_rss_du_jour(url):
    # Obtenez la date actuelle
    date_actuelle = datetime.now(timezone.utc) - timedelta(days=1)
    print(f"\nDate de recupération flux : {date_actuelle}")

    # Analyser le flux RSS à partir de l'URL
    feed = feedparser.parse(url)

    # Vérifier si le chargement du flux RSS s'est bien passé
    if feed.get('bozo_exception'):
        print("Erreur lors du chargement du flux RSS:", feed.bozo_exception)
        return None

    # Créer le corps de l'e-mail
    email_body = "Titres flux RSS du jour : \n\n"
    cpt = 0

    # Ajouter les informations pour chaque entrée dans le corps de l'e-mail
    for entry in feed.entries:
        try:
            # Convertir la date de publication de l'entrée en objet datetime
            date_publication = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
            
            # Vérifier si l'entrée a été publiée aujourd'hui
            if date_publication.date() == date_actuelle.date():
                cpt = cpt +1
                email_body += f"Titre : {entry.title}\nLien : {entry.link}\nDate de publication : {entry.published}\n\n"
                arguments = [entry.link]
                # Appeler le script Python externe avec les arguments
                subprocess.run(['python', 'get_avis_cert.py'] + arguments)
        except ValueError as e:
            print(f"Erreur lors de la conversion de la date : {e}")
    print(f"\n {cpt} Avis publiés")

    return email_body

def envoyer_email_outlook(corps_email):
    outlook = win32.Dispatch('Outlook.Application')
    mail = outlook.CreateItem(0)  # 0 représente le type de courrier (olMailItem)
    
    # Définir le format du corps du courrier comme texte brut
    mail.BodyFormat = 1  # 1 représente le format texte brut (olFormatPlain)

    # Remplacez les détails du destinataire par les vôtres
    destinataire = 'pascal.dugue@capgemini.com'

    mail.Subject = 'Titres du flux RSS du jour'
    mail.Body = corps_email
    mail.To = destinataire
    mail.Send()



if __name__ == "__main__":
    # Remplacez l'URL par l'URL du flux RSS que vous souhaitez récupérer
    url_du_flux_rss = "https://www.cert.ssi.gouv.fr/feed/"

    # Récupérer le corps de l'e-mail
    corps_email = recuperer_flux_rss_du_jour(url_du_flux_rss)

    if corps_email:
        # Envoyer l'e-mail avec Outlook
        #envoyer_email_outlook(corps_email)
        # Vos informations d'identification Gmail
        email_address = "pdu.python@gmail.com"
        password = "lxzo pcpo zpvt gwio		"

        # Destinataire
        to_email_address = "pascal.dugue@gmail.com"

        # Créer le message
        subject = "Sujet de l'e-mail"
        body = "Contenu de l'e-mail"

        message = MIMEMultipart()
        message['From'] = email_address
        message['To'] = to_email_address
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        # Se connecter au serveur SMTP de Gmail
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email_address, password)

            # Envoyer l'e-mail
            server.sendmail(email_address, to_email_address, message.as_string())

        print("E-mail envoyé avec succès.")
    
