#!/usr/bin/python3.9

import os
import subprocess
import grp
import pwd


GREEN = '\033[92m'
RESET = '\033[0m'

def afficher_menu():
    print()
    print("Menu Apache:")
    print("1. Ajouter une page WEB par défaut")
    print("2. Autoriser les utilisateurs à déployer leurs sites")
    print("3. Ajouter une authentification simple (SITE WEB PAR DEFAUT)")
    print("4. Ajouter le SSL (SITE WEB PAR DEFAUT)")
    print("5. Création VittualHost")
    print("6. Mettre le Record du VittualHost dans le fichier DNS")
    print("7. Ajouter les utilisateurs pouvant s'authentifier au site")
    print("8. Quitter")

def action_option1():
    
    # Changer de répertoire
    try:
        os.chdir("/var/www/html")
        
        # Contenu du fichier index.html
        contenu_html = """
<html lang="fr">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width" />
    <title>Ma page de test</title>
</head>
<body>
    <h1>MA PAGE PAR DEFAUT</h1>
</body>
</html>
"""
        
        # Écrire le contenu dans le fichier index.html
        with open("index.html", "w") as fichier:
            fichier.write(contenu_html)
        
        print("Le fichier index.html a été créé avec succès. Rendez vous à : http://127.0.0.1/")
    
        # Redémarrer les services si aucune erreur n'est survenue
        gerer_services()

    except FileNotFoundError:
        print("Le répertoire /var/www/html n'existe pas.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

def creer_dossiers_web_automatiquement(nom_dossier):
    # Chemin de base pour les dossiers utilisateur
    base_path = "/home"

    # Nom du groupe Apache (assurez-vous que ce groupe existe sur votre système)
    apache_group = "apache"

    # Nom du dossier qu'on déploie pour les utilisateurs perso public_html ou web par exemple
    WEB_FOLDER = nom_dossier
    # Vérifier si le groupe apache existe
    try:
        grp.getgrnam(apache_group)
    except KeyError:
        print(f"Le groupe {apache_group} n'existe pas. Veuillez le créer ou modifier le script pour utiliser un groupe différent.")
        exit(-1)

    # Parcourir les dossiers dans /home
    for username in os.listdir(base_path):
        user_path = os.path.join(base_path, username)
        web_path = os.path.join(user_path, WEB_FOLDER)

        # Vérifier si c'est un dossier d'utilisateur et si le dossier web n'existe pas
        if os.path.isdir(user_path) and not os.path.exists(web_path):
            try:
                
                # Ici, le script va naturellement filtre les dossiers appartant des utilisateurs ou non.
                # Le fait qu'on est mis le login de l'utilsiateur comme nom de dossier permet à la méthode
                # getpwnam d'obtenir des informations sur l'utilisateur. Par contre, si un dossier perso
                # d'un utilisateur n'est pas du même nom que son login, ça ne le créera pas. Normalement,
                # ça doit toujours correspondre au login
                # Obtenir l'UID et le GID
                uid = pwd.getpwnam(username).pw_uid
                gid = grp.getgrnam(apache_group).gr_gid

                # Créer le dossier web
                os.mkdir(web_path)

                # Changer le propriétaire et le groupe du dossier web
                os.chown(web_path, uid, gid)

                os.chmod(web_path, 0o750)

                # Créer le fichier index.html
                with open(os.path.join(web_path, "index.html"), 'w') as file:
                    file.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Bienvenue à toi {username}</title>
</head>
<body>
  <h1>Bienvenue à toi {username} !</h1>
  <p> Le site pour l'examen d'admin sys linux 2024 </p>
</body>
</html>""")

                # Changer le propriétaire et le groupe du fichier index.html
                os.chown(os.path.join(web_path, "index.html"), uid, gid)

                print(f"Dossier web créé pour l'utilisateur : {username}")
            except Exception as e:
                print(f"\033[93mAvertissement : Impossible de créer le dossier 'web' pour le dossier '{username}' dans /home. \nVérifiez si '{username}' est un utilisateur valide car il n'a pas été détecté comme un dossier classique : {e}\033[0m")

def action_option2():

    # Demander si l'utilisateur a déjà modifié le fichier userdir.conf
    modifie_userdir = input("Avez-vous déjà modifié le fichier userdir.conf (o/n) ? ").lower()

    nom_dossier = ''
    
    # Si l'utilisateur n'a pas déjà modifié le fichier
    if modifie_userdir != 'o':
        # Demander le nom du dossier à l'utilisateur
        print(f"\033[93mAttention de ne pas se tromper sinon il faudra aller modifier le fichier à la main\033[0m")
        nom_dossier = input("Entrez le nom du dossier à créer dans le dossier personnel de l'utilisateur : ")


        # Modifier le fichier userdir.conf
        fichier_userdir = '/etc/httpd/conf.d/userdir.conf'
        try:
            with open(fichier_userdir, 'r') as fichier:
                lignes = fichier.readlines()

            with open(fichier_userdir, 'w') as fichier:
                for ligne in lignes:
                    if 'UserDir disabled' in ligne:
                        fichier.write('#' + ligne)
                    elif 'UserDir public_html' in ligne:
                        fichier.write('UserDir ' + nom_dossier + '\n')
                    elif '<Directory "/home/*/public_html">' in ligne:
                    # Remplacer par le nouveau chemin du répertoire
                        fichier.write('<Directory "/home/*/' + nom_dossier + '">\n')
                    else:
                        fichier.write(ligne)
            
            print(f"\033[92mLe fichier {fichier_userdir} a été modifié avec succès.\033[0m")

        except Exception as e:
            print(f"Une erreur s'est produite lors de la modification du fichier {fichier_userdir} : {e}")
    else:
        # Utiliser le nom de dossier indiqué par l'utilisateur
        nom_dossier = input("Entrez le nom du dossier déjà indiqué dans le fichier userdir.conf : ")

    choix = input("Souhaitez-vous ajouter des dossiers personnels manuellement (m) ou par script (s) ? [m/s] : ").lower()

    acl_apply = False

    if choix == 'm':
        while True:
            nom_utilisateur = input("Entrez le nom de l'utilisateur (ou tapez 'exit' pour quitter) : ")
            print("\033[93m Attention ! Dasns tous les cas, appuyer sur 'exit' appliquer les modifications\033[0m")
            if nom_utilisateur.lower() == 'exit':
                break

            try:
                # Vérifier si l'utilisateur existe
                uid = pwd.getpwnam(nom_utilisateur).pw_uid
                gid = grp.getgrnam("apache").gr_gid

                acl_apply = True

                chemin_utilisateur = f"/home/{nom_utilisateur}"
                if not os.path.exists(chemin_utilisateur):
                    print(f"\033[93mLe dossier de l'utilisateur {nom_utilisateur} n'existe pas.\033[0m")
                    continue

                chemin_dossier = os.path.join(chemin_utilisateur, nom_dossier)

                if not os.path.exists(chemin_dossier):
                    acl_apply = True
                    os.mkdir(chemin_dossier)
                    os.chmod(chemin_dossier, 0o750)
                            # Créer le fichier index.html
                    with open(os.path.join(chemin_dossier, "index.html"), 'w') as file:
                        file.write(f"""<!DOCTYPE html>
                            <html lang="en">
<head>
<meta charset="utf-8">
<title>Bienvenue à toi {nom_utilisateur}</title>
</head>
<body>
<h1>Bienvenue à toi {nom_utilisateur} !</h1>
<p> Le site pour l'examen d'admin sys linux 2024 </p>
</body>
</html>""")
                # Changer le propriétaire et le groupe du fichier index.html
                    os.chown(os.path.join(chemin_dossier, "index.html"), uid, gid)

                    print(f"Dossier {nom_dossier} créé pour l'utilisateur {nom_utilisateur}.")
                else:
                    print(f"\033[93mLe dossier {nom_dossier} existe déjà pour l'utilisateur {nom_utilisateur}.\033[0m")
                    acl_apply = True
            except KeyError:
                print(f"\033[91mL'utilisateur {nom_utilisateur} n'existe pas.\033[0m")
                continue
            
    elif choix == 's':
        creer_dossiers_web_automatiquement(nom_dossier)

    if acl_apply:
        print("\033[96mApplication des ACLs...\033[0m")
        subprocess.run("setfacl -m d:u:apache:x -m d:g:apache:x /home", shell=True)
        subprocess.run("setfacl -m u:apache:x -m g:apache:x /home/*", shell=True)
        subprocess.run(f"setfacl -m d:u:apache:rx -m d:g:apache:rx -m u:apache:rx -m g:apache:rx /home/*/{nom_dossier}", shell=True)
        print("\033[92mConfiguration terminée avec succès.\033[0m")
    
    # Redémarrer les services si aucune erreur n'est survenue
    gerer_services()

def action_option3():
    # Demander à l'utilisateur l'emplacement pour le fichier .htaccess
    emplacement_htaccess = input("Entrez l'emplacement pour le fichier .htaccess : ")

    # Modifier le fichier /etc/httpd/conf.d/welcome.conf
    fichier_welcome_conf = '/etc/httpd/conf.d/welcome.conf'
    nouveau_chemin = "/var/www/html/"  #Le chemin racine pour notre site
    modification_effectuee = False  # Variable pour suivre si la modification a été effectuée
    require_granted_ajoute = False  # Variable pour suivre si "Require all granted" a déjà été ajouté

    try:
        with open(fichier_welcome_conf, 'r') as fichier:
            lignes = fichier.readlines()

        with open(fichier_welcome_conf, 'w') as fichier:
            for ligne in lignes:
                if '<Directory /urs/share/httpd/noindex>' in ligne:
                    # Modifier le chemin et AllowOverride
                    fichier.write(f'<Directory {nouveau_chemin}>\n')
                    fichier.write('    AllowOverride All\n')
                    fichier.write('    Require all granted\n')
                    modification_effectuee = True
                elif modification_effectuee and 'AllowOverride' in ligne:
                    # Si la modification a été effectuée et que la ligne contient 'AllowOverride', la sauter
                    continue
                elif modification_effectuee and 'Require all granted' in ligne:
                    # Si "Require all granted" a déjà été ajouté, la sauter
                    require_granted_ajoute = True
                    continue
                else:
                    fichier.write(ligne)

            # Ajouter "Require all granted" si ce n'est pas déjà fait
            if modification_effectuee and not require_granted_ajoute:
                fichier.write('    Require all granted\n')

        print(f"Le fichier {fichier_welcome_conf} a été modifié avec succès.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la modification du fichier {fichier_welcome_conf} : {e}")
        return

    # Créer le fichier .htaccess
    fichier_htaccess = os.path.join(emplacement_htaccess, '.htaccess')
    try:
        with open(fichier_htaccess, 'w') as fichier:
            # Ajouter le contenu dans le fichier .htaccess
            contenu_htaccess = """
            AuthType Basic
            AuthName "Message affiché par le navigateur"
            AuthBasicProvider file
            AuthUserFile "/etc/httpd/apacheUsers.passwd"
            Require valid-user
            """
            fichier.write(contenu_htaccess)
    except Exception as e:
        print(f"Une erreur s'est produite lors de la création du fichier {fichier_htaccess} : {e}")
        return

    print(f"Le fichier {fichier_htaccess} a été créé avec succès.")

    # Lancer le script Python depuis le répertoire Documents
    script_autre = '/root/Documents/SCRIPTS/APACHE/createApacheUser.py'  # Remplacez par le chemin complet de votre script
    try:
        os.system(f"python3 {script_autre}")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'exécution du script Python : {e}")

    # Redémarrer les services si aucune erreur n'est survenue
    gerer_services()



def action_option4():
   # Ouvrir le dossier des certificats
    subprocess.Popen(['nautilus', '/etc/pki/tls/certs'])

    # Ouvrir le dossier des clés privées
    subprocess.Popen(['nautilus', '/etc/pki/tls/private'])

    # Attendre la saisie de l'utilisateur pour continuer
    confirmation = input("Certificats ajoutés ? '\033[92myes\033[0m' pour continuer : ")
    
    if confirmation.lower() != 'yes':
        print("Ajout du SSL annulé.")
        return

    print(f"Attention à ne pas se tromper dans les noms, sinon il faudra éditer le fichier à la main !")

    # Demander l'URL du site
    url_site = input("Entrez l'URL du site : ")

    # Demander le nom du certificat principal
    certificat_principal = input("Entrez le nom du fichier du certificat principal : ")

    # Demander le nom du certificat intermédiaire
    certificat_intermediaire = input("Entrez le nom du fichier  du certificat intermédiaire '\033[92mLaisser vide si il n'y en a pas!\033[0m' : ")

    # Demander le nom de la clé privée
    cle_privee = input("Entrez le nom du fichier de la clé privée : ")

    modifier_ssl_conf(url_site, certificat_principal, cle_privee, certificat_intermediaire)

def modifier_ssl_conf(url_site, certificat_principal, cle_privee, certificat_intermediaire):
    fichier_ssl_conf = '/etc/httpd/conf.d/ssl.conf'
    nouveau_contenu = []

    try:
        with open(fichier_ssl_conf, 'r') as fichier:
            lignes = fichier.readlines()

        for ligne in lignes:
            # Changer _default_ de VirtualHost par url_site
            if '_default_' in ligne and 'VirtualHost' in ligne:
                ligne = ligne.replace('_default_', url_site)

            # Changer la valeur localhost.crt dans SSLCertificateFile par certificat_principal
            elif 'SSLCertificateFile' in ligne and 'localhost.crt' in ligne:
                ligne = ligne.replace('localhost.crt', certificat_principal)

            # Changer la valeur de localhost.key dans SSLCertificateKeyFile par cle_privee
            elif 'SSLCertificateKeyFile' in ligne and 'localhost.key' in ligne:
                ligne = ligne.replace('localhost.key', cle_privee)

            # Si certificat_intermediaire est différent de vide, décommenter #SSLCertificateChainFile
            # et changer server-chain.crt par certificat_intermediaire
            elif 'SSLCertificateChainFile' in ligne and 'server-chain.crt' in ligne and certificat_intermediaire:
                ligne = ligne.replace('#SSLCertificateChainFile', 'SSLCertificateChainFile')
                ligne = ligne.replace('server-chain.crt', certificat_intermediaire)

            nouveau_contenu.append(ligne)

        with open(fichier_ssl_conf, 'w') as fichier:
            for ligne in nouveau_contenu:
                fichier.write(ligne)

        print(f"Le fichier {fichier_ssl_conf} a été modifié avec succès. Rendez-vous sur https://{url_site}")

        # Redémarrer les services si aucune erreur n'est survenue
        gerer_services()
    except Exception as e:
        print(f"Une erreur s'est produite lors de la modification du fichier {fichier_ssl_conf} : {e}")
        return
    


def creer_dossier_web(nom_dossier_web) -> bool:
    dossier_web = f"/var/www/{nom_dossier_web}"
    if not os.path.exists(dossier_web):
        os.makedirs(dossier_web)
        subprocess.run(f"setfacl -m d:u:apache:rx -m d:g:apache:rx -m u:apache:x -m g:apache:x {dossier_web}/", shell=True, stdout=subprocess.PIPE)
        # Création du fichier index.html
        with open(f"{dossier_web}/index.html", "w") as file:
            file.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{nom_dossier_web}</title>
</head>
<body>
  <h1>Bienvenue sur {nom_dossier_web} </h1>
  <p> Le site pour l'examen d'admin sys linux 2024 </p>
</body>
</html>""")
        return True;
    else:
        print(f"\n\033[91mUn dossier existe déjà sous le nom /var/www/{nom_dossier_web}. Veuillez choisir un autre nom.\033[0m")
        return False;

def demander_adresses_ip(useSSL:bool):
    adresses_ip_brutes = input("Entrez les adresses IP pour le VirtualHost (séparées par des espaces): ")
    port = ":443" if useSSL else ":80"
    return ' '.join([ip + port for ip in adresses_ip_brutes.split()])

def generer_vhost_sans_tls(nom_fichier, adresses_ip, server_name, dossier_web, authentification, server_aliases):
    # 7. Créer le contenu du fichier VirtualHost
    contenu_vhost = f"<VirtualHost {adresses_ip}>\n"
    contenu_vhost += f"\tServerName {server_name}\n"
    for alias in server_aliases:
        contenu_vhost += f"\tServerAlias {alias}\n"
    contenu_vhost += f"\tDocumentRoot {dossier_web}/\n"
    contenu_vhost += f"\t<Directory \"{dossier_web}/\">\n"
    if authentification:
        contenu_vhost += "\t\tAllowOverride All\n"
    contenu_vhost += "\t\tRequire all granted\n"
    contenu_vhost += "\t</Directory>\n"
    contenu_vhost += f"\tErrorLog logs/{nom_fichier}_error_log\n"
    contenu_vhost += f"\tCustomLog logs/{nom_fichier}_access_log combined\n"
    contenu_vhost += "</VirtualHost>\n"
    return contenu_vhost;

def generer_vhost_avec_tls(nom_fichier, adresses_ip, server_name, dossier_web, authentification, tls_info, server_aliases):
    nom_certificat_domaine, nom_cle, nom_certificat_intermediaire = tls_info
    contenu_vhost = f"<VirtualHost {adresses_ip}>\n"
    contenu_vhost += f"\tServerName {server_name}\n"
    for alias in server_aliases:
        contenu_vhost += f"\tServerAlias {alias}\n"
    contenu_vhost += f"\tDocumentRoot {dossier_web}/\n"
    contenu_vhost += f"\tLogLevel warn\n"
    contenu_vhost += f"\tErrorLog logs/{nom_fichier}_error_log\n"
    contenu_vhost += f"\tTransferLog logs/{nom_fichier}_access_log\n"
    contenu_vhost += f"\t<Directory \"{dossier_web}/\">\n"
    if authentification:
        contenu_vhost += "\t\tAllowOverride All\n"
    contenu_vhost += "\t\tRequire all granted\n"
    contenu_vhost += "\t</Directory>\n"
    contenu_vhost += "\n\tSSLEngine on\n"
    contenu_vhost += "\tSSLProtocol all -SSLv2 -SSLv3 -TLSv1 -TLSv1.1 -TLSv1.2\n"
    contenu_vhost += "\tSSLHonorCipherOrder off\n"
    contenu_vhost += "\tSSLSessionTickets off\n"
    contenu_vhost += f"\tSSLCertificateFile /etc/pki/tls/certs/{nom_certificat_domaine}\n"
    contenu_vhost += f"\tSSLCertificateKeyFile /etc/pki/tls/private/{nom_cle}\n"
    contenu_vhost += f"\tSSLCertificateChainFile /etc/pki/tls/certs/{nom_certificat_intermediaire}\n"
    contenu_vhost += f'\tCustomLog logs/{nom_fichier}_ssl_request_log \\\n\t"%t %h %{{SSL_PROTOCOL}}x %{{SSL_CIPHER}}x \\"%r\\" %b"\n'
    contenu_vhost += "</VirtualHost>\n"
    return contenu_vhost


def configurer_tls():
    print("Veuillez vous assurer que les certificats TLS sont correctement placés.")


    subprocess.Popen(['nautilus', '/etc/pki/tls/certs/'])
    subprocess.Popen(['nautilus', '/etc/pki/tls/private/'])
    subprocess.Popen(['nautilus', '/root/Downloads/'])
    
    print("Êtes-vous sûr que les certificats soient correctements placés ? (o/n) ")
    nom_certificat_domaine = input("Entrez le nom du fichier de votre certificat \033[96mprincipal\033[0m (pas intermédiaire !!!) TLS avec extension (exemple : intra.crt): ")
    nom_cle = input("Entrez le nom de votre fichier de la clé privée TLS avec extension  (exemple : intra.key): ")
    nom_certificat_intermediaire = input("Entrez le nom de votre fichier de certificat \033[92mintermédiaire\033[0m TLS avec extension (exemple : ggssl.crt): ")


    # appliquer les droits chmod 0600 sur la clé
    cmd_chemin_cle = f"chmod 0600 /etc/pki/tls/private/{nom_cle}"
    subprocess.run(cmd_chemin_cle, shell=True, stdout=subprocess.PIPE)
    return nom_certificat_domaine, nom_cle, nom_certificat_intermediaire

def demander_server_alias():
    server_aliases = []
    while True:
        alias = input("Alias du site (autre url pour accéfer à celui-ci) (Enter pour ne pas en mettre) :")
        if alias:
            server_aliases.append(alias)
        else:
            break
    return server_aliases


def action_option5():
    # 1. Demander le nom du fichier
    nom_fichier = input("Nom du fichier VirtualHost (sans .conf): ")
    chemin_fichier = f"/etc/httpd/conf.d/{nom_fichier}.conf"

    # Vérifier si le fichier de configuration existe déjà
    if os.path.exists(chemin_fichier):
        print(f"\033[91mUn fichier de configuration existe déjà sous le nom {nom_fichier}.conf. Veuillez choisir un autre nom.\033[0m")
        return

    # 2. Créer le dossier pour les pages web
    nom_dossier_web = input("Nom du dossier pour contenir votre site dans (/var/www/html): ")
    if not creer_dossier_web(nom_dossier_web):
        return
    dossier_web = f"/var/www/{nom_dossier_web}"

    # 3. Demander si le site utilise TLS
    utilise_tls = input("Activer le SSL (o/n) : ").lower()
    useSSL = utilise_tls == 'o'

    # 4. Demander les adresses IP pour le VirtualHost
    adresses_ip = demander_adresses_ip(useSSL)

    # 5. Demander le ServerName
    server_name = input("URL que vous souhaitez pour accéder au site: ")

    # 5.1 Demander si ServerAlias
    server_aliases = demander_server_alias()

    # 6. Demander si une authentification est nécessaire
    authentification = input("Activer l'authentification (o/n) : ")
    useAuth = authentification == 'o'

    contenu_vhost = None

    # 7. Créer le contenu du fichier VirtualHost
    if not useSSL:
        contenu_vhost = generer_vhost_sans_tls(nom_fichier, adresses_ip, server_name, dossier_web, useAuth, server_aliases)
    else:
        tls_info = configurer_tls()
        contenu_vhost = generer_vhost_avec_tls(nom_fichier, adresses_ip, server_name, dossier_web, useAuth, tls_info, server_aliases)


    # Écrire dans le fichier de configuration
    with open(chemin_fichier, 'w') as fichier:
        fichier.write(contenu_vhost)

    gerer_services()

    print(f"\nVirtualHost créé à l'emplacement : {chemin_fichier}")
    print(f"Dossier créer à l'emplacement : {dossier_web}")

    if useAuth:
        print(f"Ton site est prêt à accueillir une authentification. Pour la mettre en place automatiquement, (option 7) ")
        
    print(f"Si ce n'est pas déjà fait, ajouter le site aux entrées DNS ! (option 6)")

def verifier_fichier_zone_existe(nom_zone):
    fichier_zone = f"/var/named/chroot/var/named/{nom_zone}"
    if not os.path.exists(fichier_zone):
        print(f"\n\033[91m Le fichier de zone {nom_zone} n'existe pas dans /var/named/chroot/var/named/\033[0m")
        return False
    else:
        print(f"\n\033[92mFichier de zone :  {nom_zone} est valide.\033[0m")
        return True
    
def demander_adresses_ip_dns():
    adresses_ip_str = input("La ou les addresses IP pour où tourne Apache (séparées par un espace) : ")
    adresses_ip = adresses_ip_str.split()
    return adresses_ip

def restart_named_chroot_service():
    try:
        # Vérifier si le service est actif
        status_process = subprocess.run(['systemctl', 'is-active', 'named-chroot'], capture_output=True, text=True)
        status = status_process.stdout.strip()

        if status == 'active':
            # Si le service est actif, le redémarrer
            subprocess.run(['systemctl', 'restart', 'named-chroot'])
            print("Le service named-chroot a été redémarré.")
        else:
            # Si le service n'est pas actif, l'activer et le démarrer
            subprocess.run(['systemctl', 'enable', '--now', 'named-chroot'])
            print("Le service named-chroot a été activé et démarré.")

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

def action_option6():
    nom_zone = input("Nom du fichier contenant vos entrées DNS : ")
    if not verifier_fichier_zone_existe(nom_zone):
        return
    nom_site = input("Entrer le nom du site sans le nom de domaine : ")
    adresses_ip = demander_adresses_ip_dns()

    # Ouverture du fichier de zone en mode append
    fichier_zone = f"/var/named/chroot/var/named/{nom_zone}"
    with open(fichier_zone, 'a') as fichier:
        # Écrire la première adresse IP avec le nom du site
        fichier.write(f"{nom_site}\tIN\tA\t{adresses_ip[0]}\n")
        # Pour les adresses IP suivantes, ne pas répéter le nom du site
        for adresse in adresses_ip[1:]:
            fichier.write(f"\t\tIN\tA\t{adresse}\n")

    print(f"\nEntrée ajoutée dans la configuration DNS : /var/named/chroot/var/named/{nom_zone} .")
    restart_named_chroot_service()


def gerer_htaccess(nom_dossier_web):
    # Demander et vérifier le nom du fichier .passwd
    while True:
        nom_fichier_passwd = input("Nom de votre fichier .passwd (sans l'extension .passwd) : ")
        chemin_fichier_passwd = f"/etc/httpd/{nom_fichier_passwd}.passwd"
        if os.path.exists(chemin_fichier_passwd):
            print("\033[91mUn fichier .passwd existe déjà avec ce nom. Veuillez choisir un autre nom.\033[0m")
            continue
        else:
            break
    # Creer le fichier .passwd
    subprocess.run(f"touch {chemin_fichier_passwd}", shell=True, stdout=subprocess.PIPE)
    print(f"{GREEN}Fichier à l'emplacement {chemin_fichier_passwd} créé avec succès. N'oubliez pas de mettre ce chemin dans le script createUsersApache !{RESET}")

    # Creer le fichier .htaccess dans le dossier web
    chemin_htaccess = f"/var/www/{nom_dossier_web}/.htaccess"
    if os.path.exists(chemin_htaccess):
        print("\033[93mUn fichier .htaccess existe déjà. Merci d'aller vérifier son contenu manuellement.\033[0m")
        return   

    with open(chemin_htaccess, 'w') as htaccess_file:
             htaccess_file.write(f"""AuthType Basic
AuthName "Admin panel requires a valid account. Anonymous are not allowed"
AuthBasicProvider file
AuthUserFile "{chemin_fichier_passwd}"
Require valid-user
""")
             
    print(f"\033[92mFichier .htaccess créé avec succès : {chemin_htaccess}.\033[0m")
    print(f"\033[Activer l'option pour voir les fichiers cachés et le déplacer si on le souhaite.\033[0m")

    subprocess.Popen(["nautilus", f"/var/www/{nom_dossier_web}"])

    # Demander à l'utilisateur s'il souhaite gérer les utilisateurs manuellement ou par script
    choix_utilisateur = input("Voulez-vous ajouter les utilisateurs manuellement (m) ou par script (s) ? [m/s] : ").lower()
    if choix_utilisateur == 'm':
        while True:
            login = input("Login de l'utilisateur (ou tapez 'exit' pour quitter) : ")
            print("\033[93m Attention ! Dans tous les cas, appuyer sur 'exit' appliquer les modifications\033[0m")
            if login.lower() == 'exit':
                break
            password = input("Mot de passe de l'utilisateur : ")
            subprocess.run(f"htpasswd -Bb {chemin_fichier_passwd} {login} {password}", shell=True)

    elif choix_utilisateur == 's':
        while True:
            confirmation = input("Script createUserApache correctement modifié (o/n/exit) : ").lower()
            print("\033[93m exit pour annuler.\033[0m")
            if confirmation == 'o':
                script_add_passwd = '/root/Documents/SCRIPTS/APACHE/createUsersApache.py'  # Remplacez par le chemin complet de votre script
                try:
                    subprocess.run(["python3.9", script_add_passwd], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Une erreur s'est produite lors de l'exécution du script Python $ {script_add_passwd}: {e}")
                except Exception as e:
                    print(f"Erreur générale dans le script ${script_add_passwd} : {e}")
            elif confirmation == 'exit':
                print("\033[93Fin du script, n'oubliez d'ajouter les utilisateurs si vous le souhaitez.\033[0m")
                break  
            else:
                print("Presser 'o/exit' pour quitter.")


def action_option7():
    nom_dossier_web = input("Nom du dossier qui contient votre site dans /var/www/html :")
    chemin_dossier_web = f"/var/www/{nom_dossier_web}/"
    if not os.path.exists(chemin_dossier_web):
        print("\033[93mCe dossier n'existe pas. Merci d'entrer un dossier valide.\033[0m")
        return  
    gerer_htaccess(nom_dossier_web)
    gerer_services()

    

def choix_utilisateur():
    try:
        choix = int(input("Choisissez une option (1-8): "))
        print()  # Ajoute une ligne vide
        return choix
    except ValueError:
        print("Veuillez entrer un nombre valide.")
        return None
    

def gerer_services():
    services = ["httpd", "php-fpm"]

    for service in services:
        try:
            # Vérifier l'état du service
            subprocess.run(['systemctl', 'is-active', '--quiet', service], check=True)

            # Si le service est actif, redémarrer
            subprocess.run(['sudo', 'systemctl', 'restart', service])
            print("\033[92mLes services httpd et php-form ont été redémarrés avec succès\033[0m")
        except subprocess.CalledProcessError:
            # Si le service n'est pas actif, le démarrer
            subprocess.run(['sudo', 'systemctl', 'enable', '--now', service])

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