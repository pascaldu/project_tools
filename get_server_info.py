import nmap

# Créer un objet de scanner
nm = nmap.PortScanner()

# Spécifier l'hôte à scanner
target_host = "https://www.telepac.agriculture.gouv.fr/telepac/auth/accueil.action"

# Effectuer un scan SYN sur les 1000 premiers ports
nm.scan(hosts=target_host, arguments="-sS -p 1-1000")

# Afficher les résultats du scan
for host in nm.all_hosts():
    print("----------------------------------------------------")
    print(f"Host: {host} ({nm[host].hostname()})")
    print(f"State: {nm[host].state()}")
    for proto in nm[host].all_protocols():
        print("----------")
        print(f"Protocol: {proto}")
        lport = nm[host][proto].keys()
        for port in lport:
            print(f"Port: {port}\tState: {nm[host][proto][port]['state']}")

