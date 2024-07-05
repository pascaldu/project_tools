import ipaddress
import sys

def est_adresse_ip(chaine):
    try:
        ipaddress.IPv4Address(chaine)  # Vérification pour les adresses IPv4
        return True
    except ipaddress.AddressValueError:
        pass

    try:
        ipaddress.IPv6Address(chaine)  # Vérification pour les adresses IPv6
        return True
    except ipaddress.AddressValueError:
        pass

    return False

# Initialiser une variable pour stocker l'adresse IP actuelle
adresse_ip_actuelle = ""
#nom_fichier_entree = ""
#nom_fichier_sortie = ""
# Initialiser une variable pour stocker le résultat
resultat = ""

# Vérifiez si au moins deux arguments sont fournis (nom du script + fichier d'entrée)
if len(sys.argv) < 3:
   print("Usage: python script.py fichier_entree fichier_sortie")
   sys.exit(1)

# Le premier argument (sys.argv[1]) est le fichier d'entrée
nom_fichier_entree = sys.argv[1]
# Le deuxième argument (sys.argv[2]) est le fichier de sortie
nom_fichier_sortie = sys.argv[2]

# Ouvrir le fichier d'entrée en lecture
with open(nom_fichier_entree, "r") as fichier_entree:
    lignes = fichier_entree.readlines()

# Initialiser une variable pour stocker le résultat
resultat = ""

for ligne in lignes:
    # Supprimer les espaces inutiles en début et fin de ligne
    ligne = ligne.strip()

    # Vérifier si la ligne est une adresse IP
    if est_adresse_ip(ligne):
        adresse_ip_actuelle = ligne
    elif ligne:
        # Si ce n'est pas une adresse IP, ajouter l'adresse IP actuelle devant la ligne
        resultat += f'{adresse_ip_actuelle} {ligne}\n'

# Afficher le résultat (facultatif)
print(resultat)

# Écrire le résultat dans le fichier de sortie
with open(nom_fichier_sortie, "w") as fichier_sortie:
    fichier_sortie.write(resultat)

# Vous pouvez également enregistrer le résultat dans un fichier, si nécessaire.

