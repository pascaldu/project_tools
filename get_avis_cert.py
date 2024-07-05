# -*- coding: utf-8 -*-
import unicodedata
import requests
from requests_ntlm import HttpNtlmAuth
#from office365.runtime.auth.authentication_context import AuthenticationContext
#from office365.sharepoint.client_context import ClientContext
import re
import os
from bs4 import BeautifulSoup
import sys
import json
from termcolor import colored
from colorama import init, Fore, Style
import warnings
import certifi
import warnings
import urllib3
import win32com.client as win32

# Ignorer les avertissements liés aux requêtes HTTPS non vérifiées
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

# Ignorer tous les avertissements
#warnings.filterwarnings("ignore")

# Initialize colorama on Windows
init()

from requests.auth import HTTPBasicAuth

def envoyer_email_outlook(titre_email,corps_email):
    outlook = win32.Dispatch('Outlook.Application')
    mail = outlook.CreateItem(0)  # 0 représente le type de courrier (olMailItem)

    # Définir le format du corps du courrier comme texte brut
    mail.BodyFormat = 1  # 1 représente le format texte brut (olFormatPlain)
    
    # Remplacez les détails du destinataire par les vôtres
    destinataire = 'pascal.dugue@capgemini.com'

    mail.Subject = titre_email
    mail.Body = corps_email
    mail.To = destinataire
    # Ajout de la pièce jointe
    chemin_piece_jointe = os.path.join(os.path.dirname(__file__), "avis_cert.txt")  # Chemin relatif du fichier pièce jointe
    attachment = mail.Attachments.Add(chemin_piece_jointe)
    attachment.DisplayName = titre_email  # Renommer la pièce jointe
    mail.Send()

def est_decimal(chaine):
    try:
        float(chaine)
        return '.' in chaine
    except ValueError:
        return False

url = sys.argv[1]
response = requests.get(url)
response.encoding = 'utf-8'

# Initialiser le fichier de sortie
f = open('avis_cert.txt', 'w', encoding='utf-8')
print("Traitement AVIS CERT", file=f)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # Titre
    # Extraction de l'année de l'avis
    resultat = re.search(r'-(20\d{2})-', url)
    if resultat:
        annee_extrait = resultat.group(1)
    else:
        annee_extrait = "xx"

    titre = "[AVI " +annee_extrait + "-" + url.split('-')[-1].replace('/','') + "] "+ soup.find('h1').text.strip().replace('Objet: ', '')
 
    ref_AVI = annee_extrait[-2:] + "-AVI-" + url.split('-')[-1].replace('/','')

    # Solution 
    Solution = ""
    texte = soup.find('h2', string='Solution')
    if texte:
        Solution = texte.find_next('p').text

    # Risques
    Risques = ""
    Risk_list_items=""
    Risques = soup.find('h2', string='Risque(s)')
    if Risques:
        Risques_list = Risques.find_next('ul')
        if Risques_list:
            Risk_list_items = Risques_list.find_all('li')
    else:
        print("Risque(s) : non trouvé")
    
    # Résumé
    Resume = ""
    texte = soup.find('h2', string='Résumé')
    if texte:
        Resume = texte.find_next('p').text
    else:
        print("Résumé : non trouvé")

    # Systemes affectés
    Systemes = ""
    Sys_list_items=""
    Systemes = soup.find('h2', string='Systèmes affectés')
    if Systemes:
        Systemes_list = Systemes.find_next('ul')
        if Systemes_list:
            Sys_list_items = Systemes_list.find_all('li')
    else:
        print("Systèmes affectés : non trouvé")

    # Récupérer les informations des Systemes affectés
    sys_info_list = []
    for item in Sys_list_items:
        if item is not None:
            sys_reference = str(item).replace('<li>', '').replace('</li>', '')
    
    # Trouver la balise <h2> avec le texte 'Documentation'
    Documentation = soup.find('h2', string='Documentation')

    # Find all <a> tags
    links = soup.find_all('a')
    # Initialiser une liste pour stocker les URL et les textes associés
    cve_info_list = []

    # Maintenant, nous allons rechercher les URL contenant 'www.cve.org' dans les liens extraits
    for link in links:
        href = link.get("href")
        text = link.get_text()
        cve_code = re.search(r'id=(CVE-\d{4}-\d{4,7})', text )

        if cve_code:
            # Si un match est trouvé, imprimer le code CVE
            if 'www.cve.org' in href:
                cve_info_list.append({'CVE': cve_code.group(1), 'URL': href})

    # Imprimer les résultats
    print(f"Titre : {titre}")
    print(f"<TITRE> : {titre}<@>", file=f)
    print(f"URL AVIS : {url}, Texte : {ref_AVI}")
    print(f"<URL AVIS> : {url}<@>", file=f)
    print(f"<TEXTE AVIS> : {ref_AVI}<@>", file=f)
    print(f"Résumé : {Resume}")
    print(f"<RESUME> : {Resume}<@>", file=f)
    print(f"Risques : ")
    print(f"<RISQUES> : ", file=f)

    for item in Risk_list_items:
        if item is not None:
            print(f"{str(item).replace('<li>', '').replace('</li>', '')}")
            print(f"{str(item).replace('<li>', '').replace('</li>', '')}", file=f)

    print(f"Systèmes affectés : ")
    print(f"<@><SYSTEMES AFFECTES> : ", file=f)
    for item in Sys_list_items:
        if item is not None:
            print(f"{str(item).replace('<li>', '').replace('</li>', '')}")
            print(str(item).replace('<li>', '').replace('</li>', ''), file=f)
    print(f"Solution : {Solution}")
    print(f"<@><SOLUTION> : {Solution}", file=f)
# Documentation
    print(f"Documentation :")
    print(f"<@><DOCUMENTATION> :", file=f)
    cvss_score_max = 0
    cvss_lien_max = ""
    cvss_score="??"
    cvss_score_texte_max="??"
    cvss_num_score = 0
    table_content = []
    table_content.append({
        "CVE": 'CVE',
        "URL": 'URL',
        "CVSS_Score_NVD": 'CVSS score NVD',
	"CVSS_Score_CNA" : 'CVSS score CNA',
        "Vendor": 'Vendor',
        "Product": 'Product',
        "CVSS_Num_score": 0,
        "Versions_a": 'Versions'
    })
    
# Afficher la liste des CVE avec les URL et les CVSS scores
#    for cve_info in cve_info_list:
    total_elements = len(cve_info_list)
    print(f"Traitement des URLs de l'avis : {total_elements}")
    for indice, cve_info in enumerate(cve_info_list, start=1):
        # Effacer la ligne précédente
        print("\r", end="")
        print(f"Indice : {indice}/{total_elements}",end="", flush=True)
        Versions_affected = ""
        #print(cve_info['CVE'])
        url = "https://nvd.nist.gov/vuln/detail/" + cve_info['CVE'].replace(' ','')
        print(url)
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            score = soup.find('a', class_='label')
            if score:
                cvss_score=score.get_text(strip=True)    
                if est_decimal(cvss_score.split()[0]):
                    cvss_num_score = float(cvss_score.split()[0])
                else:
                    cvss_num_score = 0
                if cvss_num_score > cvss_score_max:
                    cvss_score_max = cvss_num_score
                    cvss_lien_max = cve_info['URL'] 
                    cvss_score_texte_max = cvss_score
            # Extract score CNA
            #score = soup.find('a', class_='label')
            #cvss_num_score_cna= float(cvss_score.split()[1])
            # Utilisation d'une expression régulière pour extraire la valeur CVSS du CNA
            html_str = str(soup)
            match = re.search(r'<a .*?>(\d+\.\d+)', html_str)
            cvss_value = "0"
            if match:
                cvss_value = match.group(1)
                print("La valeur CVSS est :", cvss_value)
            else:
                print("Aucune correspondance trouvée.")

            # Sélectionner tous les éléments <b> qui contiennent les données des fournisseurs et produits
            # Find all text content that matches the pattern cpe:2.3:...
            cpe_elements = soup.find_all(string=re.compile(r'cpe:2\.3:.*'))

            # Print the matched CPE strings
            for cpe_element in cpe_elements:
                print(cpe_element.strip())

            # URL de l'API CVE
            url = "https://cveawg.mitre.org/api/cve/" + cve_info['CVE'].replace(' ','')
            # Effectuer la requête HTTP
            #print(url)
            vendor_value = ""
            product_value = ""
            Versions_affected = ""

            response = requests.get(url, verify=False)
            #print(response.text)
            # Vérifier si la requête a réussi (statut 200 OK)
            if response.status_code == 200:
                # Charger le JSON à partir de la réponse
                if response.text:
                    try:
                        data = response.json()
                        # Vérifier la présence de la clé "state" avec la valeur "RESERVED"
                        if 'state' in data and data['state'] == 'RESERVED':
                            vendor_value="RESERVED"
                            product_value = "RESERVED"
                            Versions_affected = "RESERVED"
                        else:
                            # Accéder à la valeur du champ "vendor"
                            vendor_value = data['containers']['cna']['affected'][0]['vendor']
                            # Accéder à la valeur du champ "product"
                            product_value = data['containers']['cna']['affected'][0]['product']
                            # Accéder aux versions affectées
                            affected_versions = data.get("containers", {}).get("cna", {}).get("affected", [])
                            for affected_product in affected_versions:
                                product_name = affected_product.get("product")
                                vendor_name = affected_product.get("vendor")
                                for version_info in affected_product.get("versions", []):
                                    version_number = version_info.get("version")
                                    less_than = version_info.get("lessThan", "N/A")
                                    if len(Versions_affected) < 80:
                                        Versions_affected = Versions_affected + version_number + " Less than " + less_than+","
                    except Exception as e:
                        # En cas d'erreur lors du chargement du JSON
                        print("Erreur lors du chargement du JSON:", e)
                        #print("Contenu de la réponse:", response.text)
                else:
                    print("La réponse json est vide")
            else:
                print(f"Erreur lors de la requête {url}. Statut :", response.status_code)
#                print(f"CVE : {cve_info['CVE']} , URL : {cve_info['URL']}, CVSS Score :{cvss_score}, Vendor : {vendor_value}, Product : {product_value}")

            table_content.append({
                "CVE": cve_info['CVE'],
                "URL": cve_info['URL'],
                "CVSS_Score_NVD": cvss_score,
                "CVSS_Score_CNA": cvss_value,
                "Vendor": vendor_value,
                "Product": product_value,
                "CVSS_Num_score": cvss_num_score,
                "Versions_a": Versions_affected
            })
    
    print("\033[F\033[K", end="")
    # Trier le tableau par ordre décroissant de CVSS_Score
    table_content[1:] = sorted(table_content[1:], key=lambda x: x["CVSS_Score_NVD"], reverse=True)

    # Calcul de la largeur maximale pour chaque colonne
    column_widths = {
        'CVE': max(len(str(item['CVE'])) for item in table_content),
        'URL': max(len(str(item['URL'])) for item in table_content),
        'CVSS_Score_NVD': max(len(str(item['CVSS_Score_NVD'])) for item in table_content),
        'CVSS_Score_CNA': max(len(str(item['CVSS_Score_CNA'])) for item in table_content),
        'Vendor': max(len(str(item['Vendor'])) for item in table_content),
        'Product': max(len(str(item['Product'])) for item in table_content),
        'Versions_a' : max(len(str(item['Versions_a'])) for item in table_content)
    }
    
    # Affichage du tableau
    separator_line = "+--" + (column_widths['CVE']* '-') + "+--" + (column_widths['URL'] * '-')+ "+--" + (column_widths['CVSS_Score_NVD'] * '-')+ "+--" + (column_widths['CVSS_Score_CNA'] * '-')+ "+--" + (column_widths['Vendor'] * '-')+ "+--" + (column_widths['Product'] * '-')+ "+--" + (column_widths['Versions_a'] * '-') + "+"
    print(separator_line)
    print(separator_line, file=f)
    table_header = "| CVE" + ((column_widths['CVE']-2)* ' ') + "| URL" + ((column_widths['URL']-2) * ' ')+ "| CVSS Score NVD" + ((column_widths['CVSS_Score_NVD']-13) * ' ')+ "| CVSS Score NVD" + ((column_widths['CVSS_Score_CNA']-13) * ' ')+ "| Vendor" + ((column_widths['Vendor']-5) * ' ')+ "| Product" + ((column_widths['Product']-6) * ' ')+ "| Versions" + ((column_widths['Versions_a']-7) * ' ')+"|"
    print(table_header)
    print(separator_line)

    for item in table_content:
        mystr="| "+ item['CVE'] + (column_widths['CVE'] - len(str(item['CVE']))) * ' '+ " | " + item['URL'] + (column_widths['URL'] - len(str(item['URL']))) * ' '+ " | " + item['CVSS_Score_NVD'] + (column_widths['CVSS_Score_NVD'] - len(str(item['CVSS_Score_NVD']))) * " " + " | " + item['CVSS_Score_CNA'] + (column_widths['CVSS_Score_CNA'] - len(str(item['CVSS_Score_CNA']))) * " " + " | " + item['Vendor'] + (column_widths['Vendor'] - len(str(item['Vendor']))) * ' '+ " | " + item['Product'] + (column_widths['Product'] - len(str(item['Product']))) * ' '+ " | " + item['Versions_a'] + (column_widths['Versions_a'] - len(str(item['Versions_a']))) * ' '+" |"
        if item['CVSS_Score_NVD']==cvss_score_texte_max:
           print(f"{Style.BRIGHT}{Fore.RED}{mystr}{Style.RESET_ALL}")           
           print(mystr, file=f)
        else:
           if item['CVSS_Num_score'] > 8.5:
               print(f"{Style.BRIGHT}{Fore.MAGENTA}{mystr}{Style.RESET_ALL}")           
               print(mystr, file=f)
           else:
               if item['CVSS_Num_score'] > 7.5:
                   print(f"{Style.BRIGHT}{Fore.YELLOW}{mystr}{Style.RESET_ALL}")           
                   print(mystr, file=f)
               else:
                   print(mystr)
                   print(mystr, file=f)
        if item['CVE']=='CVE':
            print(separator_line)
            print(separator_line, file=f)
 
    print(separator_line)
    print(separator_line, file=f)
            
#    print(f"Score max : {cvss_score_max}, score_texte : {cvss_score_texte_max}, CVSS : {cvss_lien_max}")
    print(f"<@><SCORE MAX> {cvss_score_max} <@>, score_texte : {cvss_score_texte_max}, CVSS : {cvss_lien_max}", file=f)

#    print(f"Documentation : {Documentation}")
else:
    print(f"Échec de la requête avec le code d'état : {response.status_code}")


# Fermer le fichier explicitement
# Lire depuis un fichier avec l'encodage UTF-8
with open('avis_cert.txt', 'r', encoding='utf-8') as f:
    contenu = f.read()
    print(contenu)
titre="CERTFR-"+titre
if "-nm" not in sys.argv[2:]:
    envoyer_email_outlook(titre,contenu)
else:
    print("Email non envoyé")

f.close()

# Import des données dans Sharepoint
# Remplacez ces valeurs par les vôtres
site_url = "https://capgemini.sharepoint.com/sites/ASPPILOTAGE-Cybersecu"
list_name = "vulnASP"

# URL de l'endpoint REST pour la liste
endpoint_url = f"{site_url}/_api/web/lists/getbytitle('{list_name}')/items"

# Données à ajouter à la liste
data = {
    '__metadata': {'type': 'SP.Data.vulnASPListItem'},
    'Titre': {titre},  # Remplacez 'Titre' par le nom de vos colonnes
    'CVSS V3': {cvss_score_texte_max}
}

# En-têtes de la requête
#headers = {
#    'Accept': 'application/json;odata=verbose',
#    'Content-Type': 'application/json;odata=verbose',
#}

#endpoint_url ="https://capgemini.sharepoint.com/sites/ASPPILOTAGE-Cybersecu/_api/web/lists/getbytitle('vulnASP')/items"
#print(endpoint_url)

# Faire une demande HTTP avec authentification NTLM (SSO)
#response = requests.get(site_url)
# Vérifier si la demande a réussi
#if response.status_code == 200:
#    print(f"la requete SSO a réussi !")
#else:
#    print(f"Status : {response.status_code}")

#print(response)

# Effectuer la requête POST pour ajouter l'élément
#response = requests.post(endpoint_url, json=data, headers=headers, auth=auth)
#response = requests.post(endpoint_url, json=data, headers=headers, auth=auth)

# Vérifier le statut de la requête
#if response.status_code == 201:
#    print("Élément ajouté avec succès.")
#else:
#    print(f"Échec de l'ajout de l'élément. Code d'erreur : {response.status_code}")
#    print(response.text)
