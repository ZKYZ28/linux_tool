#!/usr/bin/python3.9

import os
import subprocess

BLUE = '\033[34m'
RESET = '\033[0m'

def afficher_menu():
    print()
    print(f"{BLUE}MENU FTP : {RESET}")
    print("DANS LA CONFIGURATION /etc/vsftpd/vsftpd.conf ne pas oublier de changer listen_ipv6 à NO !")
    print("1. Gérer l'accès anonyme")
    print("2. Ajouter que seul les utilsateurs autorisés puissent se connecter")
    print("3. Ajouter des utilisateurs autorisés à se connecter")
    print("4. Emprisonner les utilisateurs dans leur dossier personnel")
    print("5. Ajouter les utilisateurs pouvant sortir de leur dossier personnel")
    print("6. Activer le mode passif avec des ports spécifiques")
    print("7. Activer le SSL")
    print("8. Quitter")

def action_option1():
    try:
        # Demander à l'utilisateur s'il veut activer ou désactiver l'accès anonyme
        choix_anonyme = input("Voulez-vous activer (a) ou désactiver (d) l'accès anonyme ? ").lower()

        if choix_anonyme == 'a':
            # Activer l'accès anonyme
            config_anonyme = 'anonymous_enable=YES'
        elif choix_anonyme == 'd':
            # Désactiver l'accès anonyme
            config_anonyme = 'anonymous_enable=NO'
        else:
            print("Option invalide. Veuillez choisir 'a' pour activer ou 'd' pour désactiver.")
            return

        # Lire le contenu actuel du fichier
        with open('/etc/vsftpd/vsftpd.conf', 'r') as fichier_conf:
            lignes = fichier_conf.readlines()

        # Modifier la ligne correspondante dans la liste des lignes
        for i, ligne in enumerate(lignes):
            if ligne.startswith('anonymous_enable='):
                lignes[i] = config_anonyme + '\n'

        # Écrire le contenu modifié dans le fichier
        with open('/etc/vsftpd/vsftpd.conf', 'w') as fichier_conf:
            fichier_conf.writelines(lignes)

        gerer_services()
        print(f"L'accès anonyme a été {'' if choix_anonyme == 'a' else 'dés'}activé avec succès.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

def action_option2():
    try:
        # Vérifier si userlist_enable est déjà configuré dans le fichier
        userlist_enable_present = False

        # Lire le contenu actuel du fichier
        with open('/etc/vsftpd/vsftpd.conf', 'r') as fichier_conf:
            lignes = fichier_conf.readlines()

            for ligne in lignes:
                if ligne.startswith('userlist_enable=YES'):
                    userlist_enable_present = True
                    break

        # Si userlist_enable n'est pas configuré, l'ajouter à la fin du fichier
        if not userlist_enable_present:
            lignes.append('userlist_enable=YES\n')

        # Rechercher la position de userlist_enable dans la liste des lignes
        for i, ligne in enumerate(lignes):
            if ligne.startswith('userlist_enable='):
                # Modifier la ligne correspondante
                lignes[i] = 'userlist_enable=YES\n'
                break

        # Vérifier si les lignes existent déjà dans le fichier
        if 'userlist_deny=NO\n' not in lignes:
            lignes.append('userlist_deny=NO\n')

        if 'userlist_file=/etc/vsftpd/user_list\n' not in lignes:
            lignes.append('userlist_file=/etc/vsftpd/user_list\n')

        # Écrire le contenu modifié dans le fichier
        with open('/etc/vsftpd/vsftpd.conf', 'w') as fichier_conf:
            fichier_conf.writelines(lignes)

        gerer_services()
        print("Les utilisateurs pouvant se connecter \033[91m(doivent être sur le système !)\033[0m peuvent maintenant être ajoutés à /etc/vsftpd/user_list .")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

def action_option3():
    try:
        # Demander à l'utilisateur s'il souhaite utiliser le script ou ajouter manuellement
        choix_script = input("Voulez-vous utiliser le script pour ajouter des utilisateurs (o/n) ? ").lower()

        if choix_script == 'o':
            # Lancer le script Python pour ajouter des utilisateurs
            subprocess.run(["python3.9", "SCRIPTS/FTP/addFTPUsers.py"])
            gerer_services()

        elif choix_script == 'n':
            # Demander à l'utilisateur d'introduire les utilisateurs séparés par des virgules
            utilisateurs_manuels = input("Introduisez les logins des utilisateurs séparés par des virgules : ").split(',')

            # Se rendre dans le fichier /etc/vsftpd/user_list et ajouter les utilisateurs
            fichier_user_list = '/etc/vsftpd/user_list'
            with open(fichier_user_list, 'a') as user_list:
                for utilisateur in utilisateurs_manuels:
                    utilisateur = utilisateur.strip()
                    if utilisateur:  # Ignorer les chaînes vides
                        user_list.write(utilisateur + '\n')

            print("Utilisateurs ajoutés avec succès en utilisant le script Python à /etc/vsftpd/user_list .")
            gerer_services()
        else:
            print("Choix invalide. Veuillez choisir 'o' pour utiliser le script ou 'n' pour ajouter manuellement.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

def action_option4():
    fichier_vsftpd_conf = "/etc/vsftpd/vsftpd.conf"
    chroot_list = "/etc/vsftpd/chroot_list"

    # Ouvrir le fichier vsftpd.conf en mode lecture
    with open(fichier_vsftpd_conf, 'r') as fichier:
        lignes = fichier.readlines()

    # Décommenter les lignes
    for i in range(len(lignes)):
        if '#chroot_local_user=YES' in lignes[i]:
            lignes[i] = lignes[i].replace('#chroot_local_user=YES', 'chroot_local_user=YES')
        elif '#chroot_list_enable=YES' in lignes[i]:
            lignes[i] = lignes[i].replace('#chroot_list_enable=YES', 'chroot_list_enable=YES')
        elif '#chroot_list_file=/etc/vsftpd/chroot_list' in lignes[i]:
            lignes[i] = lignes[i].replace('#chroot_list_file=/etc/vsftpd/chroot_list', 'chroot_list_file=/etc/vsftpd/chroot_list')
            # Ajouter allow_writable_chroot=YES à la ligne suivante
            if i + 1 < len(lignes):
                lignes[i + 1] = 'allow_writeable_chroot=YES\n'

    # Écrire les modifications dans le fichier vsftpd.conf
    with open(fichier_vsftpd_conf, 'w') as fichier:
        fichier.writelines(lignes)


    # Vérifier si le fichier pour le chroot existe
    if not os.path.exists(chroot_list):
        # Si le fichier n'existe pas, le créer
        with open(chroot_list, 'w'):
            pass  # Utilisation de 'pass' pour indiquer une opération vide

        print(f"Le fichier {chroot_list} a été créé avec succès.")

    gerer_services()
    print("Les modifications ont été apportées avec succès au fichier vsftpd.conf.")


def action_option5():
    fichier_chroot_list = "/etc/vsftpd/chroot_list"

    # Demander à l'utilisateur une liste de logins
    liste_logins = input("Entrez une liste de logins séparés par des virgules : ").split(',')

    # Ouvrir le fichier chroot_list en mode écriture (créer s'il n'existe pas)
    with open(fichier_chroot_list, 'a+') as fichier:
        # Lire les logins existants dans le fichier
        logins_existants = set(map(str.strip, fichier.readlines()))

        # Ajouter les nouveaux logins
        for login in liste_logins:
            login = login.strip()
            if login and login not in logins_existants:
                fichier.write(f"{login}\n")
                print(f"Le login '{login}' a été ajouté au fichier chroot_list.")

    gerer_services()
    print(f"Les utilisateurs ont été ajoutés avec succès : {fichier_chroot_list}")


def action_option6():
    fichier_vsftpd_conf = "/etc/vsftpd/vsftpd.conf"

    # Demander à l'utilisateur le port minimum
    pasv_min_port = input("Entrez le port minimum pour le mode passif : ")

    # Demander à l'utilisateur le port maximum
    pasv_max_port = input("Entrez le port maximum pour le mode passif : ")

    # Demander à l'utilisateur l'adresse WAN de pfSense
    pasv_address = input("Entrez l'adresse IP à utiliser (WAN pfSense si vous souhaite accéder depuis l'extérieur / IP Interface 3 Routeur si le service tourne sur le Routeur et que vous souhaitez y accéder avec le Client): ")

    # Ouvrir le fichier vsftpd.conf en mode écriture (créer s'il n'existe pas)
    with open(fichier_vsftpd_conf, 'a+') as fichier:
        # Aller à la fin du fichier et ajouter les nouvelles lignes
        fichier.write('\n')  # Ajouter une ligne vide
        fichier.write('pasv_enable=YES\n')
        fichier.write(f'pasv_min_port={pasv_min_port}\n')
        fichier.write(f'pasv_max_port={pasv_max_port}\n')
        fichier.write(f'pasv_address={pasv_address}\n')

    print("Configuration du mode passif terminée. Si jamais vous devez accéder à FTP depuis l'extérieur, ne pas oublier d'ouvrir vos ports dans pfSense !")
    print("Pour se connecter au FTP, utiliser l'adresse indiquée dans le mode passif !")
    gerer_services()
 

def action_option7():
    fichier_vsftpd_conf = "/etc/vsftpd/vsftpd.conf"
    cert_dir_certs = "/etc/pki/tls/certs/"
    cert_dir_private = "/etc/pki/tls/private/"

    # Ouvrir les répertoires avec Nautilus
    os.system(f"nautilus {cert_dir_certs}")
    os.system(f"nautilus {cert_dir_private}")

    # Demander à l'utilisateur de confirmer s'il a ajouté les certificats
    confirmation = input("Avez-vous ajouté vos certificats dans les répertoires ? (yes/no): ").lower()

    if confirmation == "yes":
        # Demander à l'utilisateur le nom du certificat principal
        certificat_principal = input("Entrez le nom de votre certificat principal (sans extension .crt) : ")

        # Demander à l'utilisateur le nom du certificat intermédiaire
        certificat_intermediaire = input("Entrez le nom de votre certificat intermédiaire (laissez vide si non applicable) (sans extension .crt) : ")

        # Demander à l'utilisateur le nom de sa clé
        nom_cle = input("Entrez le nom de votre clé (sans extension .key) : ")

        subprocess.run([f"openssl x509 -in {cert_dir_certs}{certificat_principal}.crt -out {cert_dir_certs}{certificat_principal}.pem"], shell=True, check=True)
        
        if certificat_intermediaire:
            subprocess.run([f"openssl x509 -in {cert_dir_certs}{certificat_intermediaire}.crt -out {cert_dir_certs}{certificat_intermediaire}.pem"], shell=True, check=True)

        subprocess.run([f"cat {cert_dir_certs}{certificat_principal}.pem {cert_dir_certs}{certificat_intermediaire}.pem > {cert_dir_certs}certificatsUnion.pem"], shell=True, check=True)

        subprocess.run([f"openssl rsa -in {cert_dir_private}{nom_cle}.key -out {cert_dir_private}{nom_cle}.pem"], shell=True, check=True)


         # Ouvrir le fichier vsftpd.conf en mode écriture (créer s'il n'existe pas)
        with open(fichier_vsftpd_conf, 'a+') as fichier:
            # Aller à la fin du fichier et ajouter les nouvelles lignes
            fichier.write('\n')  # Ajouter une ligne vide
            fichier.write('ssl_enable=YES\n')
            # Condition pour choisir le certificat à utiliser
            if certificat_intermediaire:
                fichier.write(f'rsa_cert_file={cert_dir_certs}certificatsUnion.pem\n')
            else:
                fichier.write(f'rsa_cert_file={cert_dir_certs}{certificat_principal}.pem\n')

            fichier.write(f'rsa_private_key_file={cert_dir_private}{nom_cle}.pem\n')

        gerer_services()
        print("Configuration SSL terminée.")
    else:
        print("Configuration SSL annulée.")

def choix_utilisateur():
    try:
        choix = int(input("Choisissez une option (1-8): "))
        print()  # Ajoute une ligne vide
        return choix
    except ValueError:
        print("Veuillez entrer un nombre valide.")
        return None

def gerer_services():
    service_name = "vsftpd"

    # Vérifier si le service est actif
    try:
        subprocess.run(["systemctl", "is-active", "--quiet", service_name], check=True)
        # Si le service est actif, le redémarrer
        subprocess.run(["systemctl", "restart", service_name], check=True)
        print(f"Le service {service_name} a été redémarré.")
    except subprocess.CalledProcessError:
        # Si le service n'est pas actif, l'activer et le démarrer
        subprocess.run(["systemctl", "enable", "--now", service_name], check=True)
        print(f"Le service {service_name} a été activé et démarré.")


def main():
    while True:
        afficher_menu()
        choix = choix_utilisateur()
        print()

        if choix is not None:
            if choix == 1:
                action_option1()
            elif choix == 2:
                action_option2()
            elif choix == 3:
                action_option3()
            elif choix == 4:
                action_option4()
            elif choix == 5:
                action_option5()
            elif choix == 6:
                action_option6()
            elif choix == 7:
                action_option7()
            elif choix == 8:
                print("Au revoir!")
                break
            else:
                print("Option invalide. Veuillez choisir une option de 1 à 8.")

if __name__ == "__main__":
    main()