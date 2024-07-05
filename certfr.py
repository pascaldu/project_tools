import requests
import pandas as pd

# Liste d'URLs CERTFR
urls_certfr = [
    "https://www.cert.ssi.gouv.fr/avis/CERTFR-2023-AVI-0628/",
    "https://www.cert.ssi.gouv.fr/avis/CERTFR-2023-AVI-0669/",
    "https://www.cert.ssi.gouv.fr/avis/CERTFR-2023-AVI-0009/",
    "https://www.cert.ssi.gouv.fr/avis/CERTFR-2023-AVI-0135/",
    "https://www.cert.ssi.gouv.fr/avis/CERTFR-2023-AVI-0103/",
    "https://www.cert.ssi.gouv.fr/avis/CERTFR-2023-AVI-0437/",
    "https://www.cert.ssi.gouv.fr/avis/CERTFR-2023-AVI-0107/",
    "https://www.cert.ssi.gouv.fr/avis/CERTFR-2022-AVI-1054/",
    "https://www.cert.ssi.gouv.fr/avis/CERTFR-2023-AVI-0378/",
    "https://www.cert.ssi.gouv.fr/avis/CERTFR-2023-AVI-0651/",
    "https://www.cert.ssi.gouv.fr/avis/CERTFR-2023-AVI-0779/",
    "https://www.cert.ssi.gouv.fr/avis/CERTFR-2023-AVI-0924/"
]

# Fonction pour extraire les informations depuis l'API CERTFR
def extraire_infos_certfr_api(url):
    api_url = f"https://api.cert.ssi.gouv.fr/v1/avis/{url.split('-')[-1]}/"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        # Exemple d'extraction de données, ajustez en fonction de la structure JSON de l'API CERTFR
        return {
            'Reference': data.get('reference'),
            'Titre': data.get('titre'),
            # Ajoutez d'autres clés en fonction des éléments à extraire
        }
    else:
        print(f"Échec de la requête pour {url}. Code d'état : {response.status_code}")
        return None

# Initialiser un DataFrame pandas pour stocker les résultats
donnees = []

# Boucle sur les URLs CERTFR
for url_certfr in urls_certfr:
    infos_certfr = extraire_infos_certfr_api(url_certfr)
    if infos_certfr:
        donnees.append(infos_certfr)

# Convertir la liste de dictionnaires en DataFrame
df = pd.DataFrame(donnees)

# Enregistrer le DataFrame au format Excel
df.to_excel('informations_certfr.xlsx', index=False)
