import requests
import csv

def get_ip_info(ip):
    response = requests.get(f"https://ipinfo.io/{ip}/json")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur lors de la récupération des informations pour {ip}: {response.status_code}")
        return None

def extract_ip_info(ip_list):
    ip_data = []
    for ip in ip_list:
        info = get_ip_info(ip.strip())
        if info:
            ip_data.append({
                'ip': ip,
                'org': info.get('org', 'N/A'),
                'country': info.get('country', 'N/A'),
                'risk': 'N/A'  # Vous pouvez ajouter une logique pour évaluer les risques si nécessaire
            })
    return ip_data

def read_ip_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def write_ip_info_to_file(ip_data, output_file):
    with open(output_file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['ip', 'org', 'country', 'risk'])
        writer.writeheader()
        for data in ip_data:
            writer.writerow(data)

if __name__ == '__main__':
    input_file = 'ips.txt'  # Le fichier texte contenant la liste des adresses IP
    output_file = 'ip_info.csv'  # Le fichier de sortie CSV avec les informations

    ip_list = read_ip_file(input_file)
    ip_data = extract_ip_info(ip_list)
    write_ip_info_to_file(ip_data, output_file)
    
    print(f"Les informations ont été écrites dans {output_file}")
