#!/usr/bin/python3.9
import os
import subprocess


# Constantes
SOURCE = "/root/Documents/SCRIPTS/OTHER/USERS/liste-utilisateurs.txt"  # Chemin vers le fichier contenant tous les utilisateurs
SPLIT = ':'  # Élément séparateur dans le fichier avec tous les utilisateurs

HTPASSFILE = "/etc/httpd/admin.passwd" #CHEMIN VERS LE FICHIER .passwd A CHANGER !!!!!!!!!!!!!!!!
HTPASSCMD = "/usr/bin/htpasswd"  

RED = '\033[91m'
GREEN = '\033[92m'
RESET = '\033[0m'


def setHtpasswd(login: str, password: str):
    cmd = f'{HTPASSCMD} -Bb {HTPASSFILE} {login} {password}'
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    if result.returncode == 0:
        return True  # Succès
    else:
        print(f"Erreur lors de l'ajout de l'utilisateur {login}: {result.stderr.decode().rstrip()}")
        return False  # Échec


# Créer le fichier HTPASSFILE s'il n'existe pas
if not os.path.exists(HTPASSFILE):
    cmd = f'touch {HTPASSFILE}'
    subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)

success_count = 0
failure_count = 0

with open(SOURCE, "r") as entree:
    for ligne in entree:
        elements = ligne.strip().split(SPLIT)

        if len(elements) == 5:
            nom, prenom, service, login, motPasse = elements

            if setHtpasswd(login, motPasse):
                success_count += 1
            else:
                failure_count += 1

        else:
            print("L'utilisateur n'a pas pu être lu dans le fichier")

if success_count > 0:
    print(f"{GREEN}{success_count} utilisateur(s) ajoutés avec succès : {HTPASSFILE} .{RESET}")
   

if failure_count > 0:
    print(f"{RED}Problème lors de l'ajout des utilisateurs  : {HTPASSFILE} !{RESET}")
