#!/usr/bin/python3.9

import os
import subprocess

MAGENTA = '\033[35m'
RESET = '\033[0m'

def afficher_menu():
    print()
    print(f"{MAGENTA}Menu MAIL :{RESET}")
    print("1. Configuration de Postfix")
    print("2. Configuration du Virtual")
    print("3. Ajouter des utilisateurs dans le  Virtual")
    print("4. Ajouter un serveur mail Backup")
    print("5. Envoyer un mail avec MailX (faire à la main pour être sûr)")
    print("6. Configuration de Dovecot")
    print("7. Quitter")



def action_option1():
    postfix_config_file = '/etc/postfix/main.cf'

    # Ouvrir le fichier de configuration en mode lecture/écriture
    with open(postfix_config_file, 'r') as file:
        lines = file.readlines()

    # Modifier les lignes nécessaires
    for i in range(len(lines)):
        if "#myhostname = virtual.domain.tld" in lines[i]:
            lines[i] = "myhostname = localhost.localdomain\n"
        elif "#mydomain = domain.tld" in lines[i]:
            lines[i] = "mydomain = localdomain\n"
        elif "inet_interfaces = localhost" in lines[i]:
            lines[i] = "inet_interfaces = all\n"
        elif "#mynetworks = hash:/etc/postfix/network_table" in lines[i]:
            # Ajouter mynetworks à la ligne suivante
            lines.insert(i + 1, "mynetworks = {}/24, 127.0.0.0/8\n".format(input("Entrez votre adresse IP d'interface numéro 3 avec comme dernière valeur 0 : ")))
        elif "#mail_spool_directory = /var/spool/mail" in lines[i]:
            lines[i] = "mail_spool_directory = /var/spool/mail\n"
       
    # Ajouter un commentaire VIRTUAL ALIAS et les lignes virtual_alias_domains et virtual_alias_maps
    lines.append("\n# VIRTUAL ALIAS\n")
    lines.append("virtual_alias_domains = {}\n".format(input("Entrez les domaines pour virtual_alias_domains, séparés par une virgule : ")))
    lines.append("virtual_alias_maps = hash:/etc/postfix/virtual\n")

    # Écrire les modifications dans le fichier
    with open(postfix_config_file, 'w') as file:
        file.writelines(lines)

    gerer_services()
    print(f"Configuration de Postfix terminée avec succès")
    print(f"\033[91mAttention de bien changer le /24 si ce n'est pas le ça : {postfix_config_file}!\033[0m")
    print("\033[91m" + "Attention de ne pas oublier d'ajouter l'entrée MX dans le fichier de zone interne du DNS et de redémarrer le service : /var/named/chroot/var/named/ :  !" + "\033[0m")
    print("\033[91m" + "Attention de bien désactiver le SSL si on le veut pas !" + "\033[0m")
    print("\033[91m" + "Attention de bien désactiver l'authentification si on ne la veut pas !" + "\033[0m")

def action_option2():
   # Ouvrir le fichier avec Vim
    subprocess.run(["vim", "/etc/postfix/virtual"])

    gerer_services()


def action_option3():
    # Demander à l'utilisateur s'il souhaite gérer les utilisateurs manuellement ou par script
    choix_utilisateur = input("Souhaitez-vous ajouter des utilisateurs manuellement (m) ou par script (s) ? [m/s] : ").lower()
    if choix_utilisateur == 'm':
        try:
            with open('/etc/postfix/virtual', 'a') as file:
                while True:
                    login = input("Entrez le login de l'utilisateur (ou tapez 'exit' pour quitter) : ")
                    if login.lower() == 'exit':
                        break

                    email = input("Entrez l'adresse mail de l'utilisateur : ")

                    # Ajouter l'entrée à la fin du fichier
                    file.write(f"{email}\t{login}\n")

            # Exécuter la commande postmap une fois que l'utilisateur a terminé
            subprocess.run(['postmap', '/etc/postfix/virtual'], check=True)
            print("Les utilisateurs ont été ajoutés avec succès.")

        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            

    elif choix_utilisateur == 's':
        confirmation = input("Avez-vous bien modifié le script pour ajouter des utilisateurs? (o/n/exit) : ").lower()
        print("\033[93Tapez exit pour annuler.\033[0m")
        if confirmation == 'o':
            script_add_users = '/root/Documents/SCRIPTS/OTHER/MAIL/createUsersVirtual.py'
            try:
                domain = input("Indiquer le nom de domain à utiliser pour les adresses mail (sans le @) : ")
                subprocess.run(["python3.9", script_add_users, domain], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Une erreur s'est produite lors de l'exécution du script Python $ {script_add_users}: {e}")
            except Exception as e:
                print(f"Erreur générale dans le script ${script_add_users} : {e}")
        else:
            print("Dès que vous êtes prêt, appuyez sur 'o' ou 'exit' pour ne rien appliquer.")




def action_option4():
    # Chemin du fichier main.cf
    main_cf_path = "/etc/postfix/main.cf"

    # Domaines pour lesquels les mails doivent être gardés
    relay_domains = input("Entrez les domaines pour lesquels les mails doivent être gardés (séparés par une virgule) : ")

    # Ouvrir le fichier de configuration en mode lecture/écriture
    with open(main_cf_path, 'r') as file:
        lines = file.readlines()

    # Modifier les lignes nécessaires
    for i in range(len(lines)):
        if "relay_domains = $mydestination" in lines[i]:
            # Ajouter mynetworks à la ligne suivante
            lines.insert(i + 1, f"relay_domains = $mydestination, {relay_domains}\n")
            lines.insert(i + 2, f"relay_recipient_maps =\n")

    # Écrire les lignes modifiées dans le fichier
    with open(main_cf_path, 'w') as file:
        file.writelines(lines)

    print("Configuration mise à jour avec succès.")


def action_option5():
    # Installer mailx si ce n'est pas déjà fait
    subprocess.run(['sudo', 'yum', 'install', '-y', 'mailx'])

    # Demander le login de l'utilisateur destinataire
    login_destinataire = input("Entrez le login de l'utilisateur destinataire : ")

    # Vérifier si le fichier existe dans /var/spool/mail
    chemin_fichier_mail = f'/var/spool/mail/{login_destinataire}'
    if not os.path.exists(chemin_fichier_mail):
        # Créer le fichier s'il n'existe pas
        subprocess.run(['sudo', 'touch', chemin_fichier_mail])
        subprocess.run(['sudo', 'chown', f'{login_destinataire}.mail', chemin_fichier_mail])
        subprocess.run(['sudo', 'chmod', '0660', chemin_fichier_mail])

    # Demander l'adresse email du destinataire
    adresse_email_destinataire = input("Entrez l'adresse email du destinataire : ")

    # Demander le sujet du mail
    sujet_mail = input("Entrez le sujet du mail : ")

    # Demander le message du mail
    message_mail = input("Entrez le message du mail : ")

    # Utiliser la commande mail pour envoyer le mail
    subprocess.run(['mail', adresse_email_destinataire], input=f'{sujet_mail}\nHello,\n{message_mail}\n.', text=True)

    print("Mail envoyé avec succès.")



def afficher_menu_dovecot():
    print()
    print("Sous-Menu Dovecot :")
    print("1. Initialiser la configuration de base de Dovecot")
    print("2. Activer/Désactiver l'authentification avec login/mot de passe")
    print("3. Activer/Désactiver le SSL")
    print("4. Retour au menu principal")

def action_option6():
    while True:
        afficher_menu_dovecot()
        choix_dovecot = choix_utilisateur()

        if choix_dovecot is not None:
            if choix_dovecot == 1:
                initialiser_configuration_dovecot()
            elif choix_dovecot == 2:
                activer_desactiver_authentification_dovecot()
            elif choix_dovecot == 3:
                activer_desactiver_ssl_dovecot()
            elif choix_dovecot == 4:
                print("Retour au menu principal.")
                break
            else:
                print("Option invalide. Veuillez choisir une option de 1 à 4.")

def initialiser_configuration_dovecot():
    # Modifier le fichier dovecot.conf
    postfix_config_file = '/etc/dovecot/dovecot.conf'

    # Ouvrir le fichier de configuration en mode lecture/écriture
    with open(postfix_config_file, 'r') as file:
        lines = file.readlines()

    # Modifier les lignes nécessaires
    for i in range(len(lines)):
        if "#protocols = imap pop3 lmtp submission" in lines[i]:
            lines[i] = "protocols = imap pop3\n"
        elif "#login_greeting = Dovecot ready." in lines[i]:
            lines[i] = "login_greeting = Godswila êtes-vous là ?\n"

    # Réécrire le fichier dovecot.conf avec les modifications
    with open(postfix_config_file, 'w') as file:
        file.writelines(lines)

    # Modifier le fichier 10-mail.conf
    mail_conf_path = "/etc/dovecot/conf.d/10-mail.conf"

    # Ouvrir le fichier de configuration en mode lecture/écriture
    with open(mail_conf_path, 'r') as file:
        lines = file.readlines()

    # Modifier les lignes nécessaires
    for i in range(len(lines)):
        if "#mail_location =" in lines[i] and "maildir:~/Maildir" not in lines[i] and "mbox:~/mail:INBOX=/var/mail/%u" not in lines[i] and "mbox:/var/mail/%d/%1n/%n:INDEX=/var/indexes/%d/%1n/%n" not in lines[i]:
            lines[i] = "mail_location = mbox:~/mail:INBOX=/var/spool/mail/%u\n"
        elif "#mail_access_groups =" in lines[i]:
            lines[i] = "mail_access_groups = mail\n"

    # Réécrire le fichier 10-mail.conf avec les modifications
    with open(mail_conf_path, 'w') as file:
        file.writelines(lines)

    gerer_services()
    print("Configuration Dovecot initialisée avec succès.")
  

def activer_desactiver_authentification_dovecot():
    # Chemin du fichier 10-auth.conf
    auth_conf_path = "/etc/dovecot/conf.d/10-auth.conf"

    # Demander à l'utilisateur s'il veut activer ou désactiver l'authentification
    choix = input("Voulez-vous activer (A) ou désactiver (D) l'authentification ? ").lower()

    # Ouvrir le fichier de configuration en mode lecture/écriture
    with open(auth_conf_path, 'r') as file:
        lines = file.readlines()

    # Modifier les lignes nécessaires
    for i in range(len(lines)):
        if "#disable_plaintext_auth = yes" in lines[i]:
            # Si l'utilisateur veut activer l'authentification, décommenter la ligne
            if choix == 'a':
                lines[i] = "disable_plaintext_auth = no\n"
            # Si l'utilisateur veut désactiver l'authentification, décommenter et modifier la ligne
            elif choix == 'd':
                lines[i] = "disable_plaintext_auth = yes\n"
        
        elif "disable_plaintext_auth = no" in lines[i]:
            # Si l'utilisateur veut activer l'authentification, décommenter la ligne
            if choix == 'a':
                lines[i] = "disable_plaintext_auth = no\n"
            # Si l'utilisateur veut désactiver l'authentification, décommenter et modifier la ligne
            elif choix == 'd':
                lines[i] = "disable_plaintext_auth = yes\n"
        
        elif "disable_plaintext_auth = yes" in lines[i]:
            # Si l'utilisateur veut activer l'authentification, décommenter la ligne
            if choix == 'a':
                lines[i] = "disable_plaintext_auth = no\n"
            # Si l'utilisateur veut désactiver l'authentification, décommenter et modifier la ligne
            elif choix == 'd':
                lines[i] = "disable_plaintext_auth = yes\n"

        elif "#auth_username_format = %Lu" in lines[i]:
            # Si l'utilisateur veut activer l'authentification, décommenter la ligne
            if choix == 'a':
                lines[i] = "auth_username_format = %Lu\n"
            # Si l'utilisateur veut désactiver l'authentification, commenter la ligne
            elif choix == 'd':
                lines[i] = "#auth_username_format = %Lu\n"

    # Réécrire le fichier 10-auth.conf avec les modifications
    with open(auth_conf_path, 'w') as file:
        file.writelines(lines)

    gerer_services()
    print("Configuration de l'authentification Dovecot mise à jour avec succès.")

def activer_desactiver_ssl_dovecot():
    # Chemin du fichier 10-ssl.conf
    ssl_conf_path = "/etc/dovecot/conf.d/10-ssl.conf"

    # Demander à l'utilisateur s'il veut activer ou désactiver SSL
    choix = input("Voulez-vous activer (A) ou désactiver (D) SSL ? ").lower()

    # Si l'utilisateur veut activer SSL, ouvrir les dossiers des certificats et des clés privées
    if choix == 'a':
        subprocess.run(['nautilus', '/etc/pki/tls/certs'])
        subprocess.run(['nautilus', '/etc/pki/tls/private'])

    # Ouvrir le fichier de configuration en mode lecture/écriture
    with open(ssl_conf_path, 'r') as file:
        lines = file.readlines()

    # Modifier les lignes nécessaires
    for i in range(len(lines)):
        if "#ssl = required" in lines[i]:
            # Si l'utilisateur veut activer SSL, décommenter la ligne
            if choix == 'a':
                lines[i] = "ssl = required\n"
            # Si l'utilisateur veut désactiver SSL, commenter la ligne
            elif choix == 'd':
                lines[i] = "#ssl = required\n"
            
        elif "ssl = required" in lines[i]:
            # Si l'utilisateur veut activer SSL, décommenter la ligne
            if choix == 'a':
                lines[i] = "ssl = required\n"
            # Si l'utilisateur veut désactiver SSL, commenter la ligne
            elif choix == 'd':
                lines[i] = "#ssl = required\n"

        elif "#ssl_cert = </etc/pki/dovecot/certs/dovecot.pem" in lines[i]:
            # Si l'utilisateur veut activer SSL, décommenter la ligne
            if choix == 'a':
                lines[i] = f"ssl_cert = </etc/pki/dovecot/certs/{input('Entrez le nom du certificat (sans le .pem) : ')}.pem\n"
            # Si l'utilisateur veut désactiver SSL, commenter la ligne
            elif choix == 'd':
                lines[i] = "#ssl_cert = </etc/pki/dovecot/certs/dovecot.pem\n"

        elif "#ssl_key = </etc/pki/dovecot/private/dovecot.pem" in lines[i]:
            # Si l'utilisateur veut activer SSL, décommenter la ligne
            if choix == 'a':
                lines[i] = f"ssl_key = </etc/pki/dovecot/private/{input('Entrez le nom de la clé (sans le .pem) : ')}.pem\n"
            # Si l'utilisateur veut désactiver SSL, commenter la ligne
            elif choix == 'd':
                lines[i] = "#ssl_key = </etc/pki/dovecot/private/dovecot.pem\n"

        elif "ssl_cert = </etc/pki/dovecot/certs/" in lines[i]:
            # Si l'utilisateur veut activer SSL, décommenter la ligne
            if choix == 'a':
                lines[i] = f"ssl_cert = </etc/pki/dovecot/certs/{input('Entrez le nom du certificat sans le .pem : ')}.pem\n"
            # Si l'utilisateur veut désactiver SSL, commenter la ligne
            elif choix == 'd':
                lines[i] = "#ssl_cert = </etc/pki/dovecot/certs/dovecot.pem\n"

        elif "ssl_key = </etc/pki/dovecot/private/" in lines[i]:
            # Si l'utilisateur veut activer SSL, décommenter la ligne
            if choix == 'a':
                lines[i] = f"ssl_key = </etc/pki/dovecot/private/{input('Entrez le nom de la clé sans le .pem : ')}.pem\n"
            # Si l'utilisateur veut désactiver SSL, commenter la ligne
            elif choix == 'd':
                lines[i] = "#ssl_key = </etc/pki/dovecot/private/dovecot.pem\n"

    # Réécrire le fichier 10-ssl.conf avec les modifications
    with open(ssl_conf_path, 'w') as file:
        file.writelines(lines)

    gerer_services()
    print("Configuration SSL Dovecot mise à jour avec succès.")


def choix_utilisateur():
    try:
        choix = int(input("Choisissez une option (1-7): "))
        print()  # Ajoute une ligne vide
        return choix
    except ValueError:
        print("Veuillez entrer un nombre valide.")
        return None

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
    
    print("Services postfix et dovecot redémarré avec succès.")

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
                print("Au revoir!")
                break
            else:
                print("Option invalide. Veuillez choisir une option de 1 à 7.")

if __name__ == "__main__":
    main()