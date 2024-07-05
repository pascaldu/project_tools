import requests
import certifi
#print(certifi.where())

url = "https://www.virustotal.com/api/v3/urls"

payload = { "url": "google.com" }
headers = {
    "accept": "application/json",
    "x-apikey": "9ac91bb6b6e393b1281e92b24099395ed433cad977d5256a9b270c5532c6ecac",
    "content-type": "application/x-www-form-urlencoded"
}

response = requests.post(url, data=payload, headers=headers)

print(response.text)