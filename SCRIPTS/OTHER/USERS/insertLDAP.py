#!/usr/bin/python3.9

import subprocess
import sys
import os

# Arguments :  "NOM" "PRENOM" UID "LOGIN" "MDP"

#CONSTANTE
GIDNUMBER = 100
SLAPCMD = "/usr/sbin/slappasswd"


def createUserDir(login: str, uid: str):
    # Vérifier si l'utilisateur possède déjà un dossier
    homeDirectory = f"/home/{login}"

    if os.path.exists(homeDirectory):
        print(f"The user {login} has already a folder")
    else:
        try:
            # Créer le répertoire
            os.mkdir(homeDirectory)

            # Définir les permissions du répertoire
            os.chmod(homeDirectory, 0o700)

            # Définir le propriétaire et le groupe du répertoire
            os.chown(homeDirectory, int(uid), GIDNUMBER)
        except OSError as e:
            print(f"Erreur lors de la création du répertoire : {e}")


#CREATION DU FICHIER POUR LES MAILS DE L'UTILISATEUR
def createMailFile(login): 
    chemin_fichier_mail = f'/var/spool/mail/{login}'
    if not os.path.exists(chemin_fichier_mail):
        # Créer le fichier s'il n'existe pas
        subprocess.run(['sudo', 'touch', chemin_fichier_mail])
        subprocess.run(['sudo', 'chown', f'{login}.mail', chemin_fichier_mail])
        subprocess.run(['sudo', 'chmod', '0660', chemin_fichier_mail])


#CHIFFREMENT DU MOT DE PASSE
def createHashPassword(password:str):
    cmd = f"{SLAPCMD} -s {password}"
    result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    return result.stdout.decode().rstrip()



# Vérifiez le nombre d'arguments en ligne de commande
if len(sys.argv) != 6:
    print("Usage: mkglobal-user.py <nom> <prenom> <UID> <login> <mot_de_passe>")
    sys.exit(1)

# Récupérez les informations de l'utilisateur à partir des arguments
nom = sys.argv[1]
prenom = sys.argv[2]
uid = sys.argv[3]
login = sys.argv[4]
mot_de_passe = sys.argv[5]
ssha_password = createHashPassword(mot_de_passe)


# Données de l'utilisateur
dn = f"uid={login},ou=People,dc=localdomain"
object_class = "inetOrgPerson"
cn = f"{prenom} {nom} (ldap)"
sn = nom
given_name = prenom
uid_number = uid
gid_number = 100 
home_directory = f"/home/{login}"
login_shell = "/bin/bash"

# Commande ldapadd avec mot de passe passé en argument
command = [
    "ldapadd",
    "-x",  # Utilise la simple authentification
    "-D", "cn=Directory Manager,dc=localdomain",
    "-w", "rootroot", # NE PAS CHANGER LE MOT DE PASSE ICI
]

# Données à ajouter
data = f"""dn: {dn}
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: top
uid: {login}
cn: {cn}
sn: {sn}
givenName: {given_name}
uidNumber: {uid_number}
gidNumber: {gid_number}
homeDirectory: {home_directory}
loginShell: {login_shell}
userPassword: {ssha_password}
"""

# Exécute la commande ldapadd avec les données passées en entrée standard
try:
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate(input=data)
    
    if process.returncode == 0:
        createUserDir(login, uid)
        createMailFile(login)
        print(f"L'utilisateur {login} a été ajouté avec succès à l'annuaire LDAP.")
except subprocess.CalledProcessError as e:
    print(f"Erreur lors de l'exécution de ldapadd : {e}")