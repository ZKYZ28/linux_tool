#!/usr/bin/python3.9

import sys
import subprocess

# Constantes
SOURCE = "/root/Documents/SCRIPTS/OTHER/USERS/liste-utilisateurs.csv"  # Chemin vers le fichier contenant tous les utilisateurs
SPLIT = ':'  # Élément séparateur dans le fichier avec tous les utilisateurs
domain = sys.argv[1]



def gerer_services():
    services = ["postfix", "dovecot"]

    for service in services:
        try:
            # Vérifier l'état du service
            subprocess.run(['systemctl', 'is-active', '--quiet', service], check=True)

            # Si le service est actif, redémarrer
            subprocess.run(['sudo', 'systemctl', 'restart', service])
        except subprocess.CalledProcessError:
            # Si le service n'est pas actif, le démarrer
            subprocess.run(['sudo', 'systemctl', 'enable', '--now', service])
    
    print("Service redémarré avec succès.")



# Créez une liste pour stocker les adresses e-mails et les logins
adresses_et_logins = []

# Créez un dictionnaire pour stocker les adresses e-mails existantes et leur fréquence
adresses_existantes = {}

with open(SOURCE, "r") as entree:
    for ligne in entree:
        elements = ligne.strip().split(SPLIT)

        if len(elements) == 5:
            nom, prenom, service, login, motPasse = elements

            # Supprimez les accents et transformez en minuscules
            prenom = prenom.lower().replace("é", "e").replace("è", "e").replace("ê", "e").replace("ë", "e").replace(
                "à", "a").replace("â", "a").replace("ä", "a").replace("î", "i").replace("ï", "i").replace("ô", "o").replace(
                "ö", "o").replace("ù", "u").replace("û", "u").replace("ü", "u").replace("ç", "c")
            nom = nom.lower().replace("é", "e").replace("è", "e").replace("ê", "e").replace("ë", "e").replace("à", "a").replace(
                "â", "a").replace("ä", "a").replace("î", "i").replace("ï", "i").replace("ô", "o").replace("ö", "o").replace(
                "ù", "u").replace("û", "u").replace("ü", "u").replace("ç", "c")

            adresse_email = f"{prenom[0]}.{nom}@{domain}"

            # Si l'adresse existe déjà, augmentez le nombre de caractères du prénom
            count = adresses_existantes.get(adresse_email, 0)
            if count > 0:
                adresse_email = f"{prenom[:count]}.{nom}@{domain}"
                count += 1
            adresses_existantes[adresse_email] = count

            adresses_et_logins.append((adresse_email, login))

try:
    with open('/etc/postfix/virtual', 'a') as file:
        for adresse, login in adresses_et_logins:
            file.write(f"{adresse}\t{login}\n")

    # Exécuter la commande postmap une fois que l'utilisateur a terminé
    subprocess.run(['postmap', '/etc/postfix/virtual'], check=True)
    
   
    print("\033[92mLes utilisateurs ont été ajoutés avec succès : /etc/postfix/virtual .\033[0m")
    gerer_services()
    
except Exception as e:
    print(f"Une erreur s'est produite : {e}")






