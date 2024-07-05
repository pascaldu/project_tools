import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Désactivez les avertissements SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Remplacez 'VOTRE_CLE_API' par votre clé d'API VirusTotal
api_key = '9ac91bb6b6e393b1281e92b24099395ed433cad977d5256a9b270c5532c6ecac'

# URL que vous souhaitez vérifier
url_to_check = 'google.com'

# URL de l'API VirusTotal pour la vérification de la réputation d'une URL
api_url = 'https://www.virustotal.com/api/v3/urls/'

# Paramètres de la requête
params = {
    'apikey': api_key,
    'resource': url_to_check
}

try:
    response = requests.get(api_url, params=params, verify=False)
    json_response = response.json()

# Traitez la réponse
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"Erreur : {response.status_code}")

#    if json_response['response_code'] == 1:
#        scan_date = json_response['scan_date']
#        positives = json_response['positives']
#        total = json_response['total']

#        print(f'URL: {url_to_check}')
#        print(f'Scan Date: {scan_date}')
#        print(f'Positive Scans: {positives}/{total}')
#        print('Scan Results:')
#        for engine, result in json_response['scans'].items():
#            print(f'{engine}: {result["result"]}')
#    else:
#        print('URL not found in VirusTotal database.')

except requests.exceptions.RequestException as e:
    print(f'Error: {e}')

except KeyError:
    print('An error occurred during the API request.')
