#!/usr/bin/python3.9

import subprocess

#<----------------------ATTENTION A BIEN CHANGER LE NOM DU FICHIER ET TOUTES LES INFORMATIONS NECESSAIRES ! ---------------------->

#CREE LE GROUPE SI IL N'EXISTE PAS DEJA
def create_local_group(service):
    # Vérifier si le groupe secondaire existe
    try:
        subprocess.run(['getent', 'group', service.lower()], check=True)
    except subprocess.CalledProcessError:
        # Le groupe n'existe pas, le créons
        try:
            subprocess.run(['sudo', 'groupadd', service.lower()])
            print(f"Groupe secondaire {service.lower()} créé avec succès.")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la création du groupe {service.lower()}: {e}")


#CREATE UN UTILISATEUR LOCAL
def create_local_user(nom, prenom, service, login, motPasse):
    if service != "compta":
        try:
            subprocess.run(['sudo', 'useradd', '-m', '-c', f'{nom} {prenom}', '-g', 'users', '-G', f'{service.lower()}', '-s', '/bin/bash', login])
            subprocess.run(['sudo', 'chpasswd'], input=f'{login}:{motPasse}', text=True, check=True)
            print(f"Utilisateur {login} créé avec succès.")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la création de l'utilisateur {login}: {e}")


#CREATE UN UTILISATEUR GOBAL
def create_gloabl_user(nom, prenom, service, login, motPasse, uid):
     if service == "compta":
                try:
                    subprocess.run(["python3.9", "insertLDAP.py", nom, prenom, str(uid), login, motPasse], check=True)
                    uid = uid + 1
                    subprocess.run(['sudo', 'usermod', '-G', service.lower(), login])
                except subprocess.CalledProcessError as e:
                    print(f"Erreur lors de l'exécution du script : {e}")


with open("liste-utilisateurs.txt", "r") as entree:   
    uid = 22500 # L'UID DE BASE POUR LES UTILISATEURS LDAP
    for ligne in entree:
        elements = ligne.strip().split(':')

        if len(elements) == 5:
            nom, prenom, service, login, motPasse = elements
            service = service.replace(" ", "_")
    
            create_local_group(service)
            create_local_user(nom, prenom, service, login, motPasse)

            uid = uid + 1
            create_gloabl_user(nom, prenom, service, login, motPasse, uid)

           