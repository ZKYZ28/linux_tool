#!/usr/bin/python3.9
import os
import subprocess
import shutil

YELLOW = '\033[33m'
RESET = '\033[0m'
GREEN = '\033[92m'
RED = '\033[91m'

def afficher_menu():
    print()
    print(f"{YELLOW}Menu DNS :{RESET}")
    print("1. Mettre en place la configuration de base")
    print("2. Ajouter des forwarders")
    print("3. Configurer l'environnement pour les fichiers des zones")
    print("4. Ajouter une zone interne")
    print("5. Ajouter une zone externe")
    print("6. Ajouter une zone inverse")
    print("7. Quitter")

def action_option1():
    try:
        # Copier les fichiers depuis /usr/share/doc/bind/sample/etc/ vers /var/named/chroot/etc/
        source_directory = "/usr/share/doc/bind/sample/etc/"
        target_directory = "/var/named/chroot/etc/"
        
        for filename in os.listdir(source_directory):
            source_path = os.path.join(source_directory, filename)
            target_path = os.path.join(target_directory, filename)
            
            # Copier uniquement si le fichier n'existe pas déjà dans le dossier cible
            if not os.path.exists(target_path):
                shutil.copy2(source_path, target_path)
                print(f"Le fichier {filename} a été copié avec succès.")

        # Modifier le fichier named.conf
        fichier_named_conf = os.path.join(target_directory, "named.conf")
        with open(fichier_named_conf, 'r') as fichier:
            lignes = fichier.readlines()
            
        with open(fichier_named_conf, 'w') as fichier:
            for ligne in lignes:
                if 'listen-on port 53' in ligne and '::1;' in ligne:
                    ligne = ligne.replace('::1;', 'any;')
                elif 'allow-query' in ligne and 'localhost;' in ligne:
                    ligne = ligne.replace('localhost;', 'any;')
                elif 'listen-on port 53' in ligne and '127.0.0.1;' in ligne:
                    ligne = ligne.replace('127.0.0.1;', 'any;')
                elif 'listen-on-v6 port 53' in ligne and '::1;' in ligne:
                    ligne = ligne.replace('::1;', 'any;')
                elif 'match-clients' in ligne and 'localnets;' in ligne and 'localnets; localhost;' not in ligne:
                    ligne = ligne.replace('localnets;', 'localnets; localhost;')
                fichier.write(ligne)

        # Supprime le bloc de la vue local
        delete_localhost_bloc(target_directory) 
        #supprime les zones de la vue interne
        delete_internal_zones(target_directory)
        # Commente le bloc ddns_key
        comment_ddns_key(target_directory)
        #supprime les zones de la vue externe
        delete_external_zones(target_directory)

        #restart_named_chroot_service()
        print(f"{GREEN}Modification du fichier réalisées avec succès : {fichier_named_conf} {RESET}")

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

def delete_localhost_bloc(target_directory):
    try:
        fichier_named_conf = os.path.join(target_directory, "named.conf")
        with open(fichier_named_conf, 'r') as fichier:
            lignes = fichier.readlines()

        with open(fichier_named_conf, 'w') as fichier:
            suppression_en_cours = False  # Variable pour indiquer si la suppression est en cours
            compteur_occurrences = 0  # Compteur d'occurrences de "};"
            
            for i, ligne in enumerate(lignes):
                # Si on trouve le début de la partie à supprimer, activer la suppression
                if 'view "localhost_resolver"' in ligne:
                    suppression_en_cours = True

                # Si on trouve la fin de la partie à supprimer, incrémenter le compteur
                elif '};' in ligne and suppression_en_cours:
                    compteur_occurrences += 1

                    # Si on atteint la troisième occurrence, désactiver la suppression
                    if compteur_occurrences == 3:
                        suppression_en_cours = False  
                        ligne = ligne.strip()
                        continue     
            

                # Si la suppression n'est pas en cours, écrire la ligne dans le fichier
                if not suppression_en_cours:
                    fichier.write(ligne)

            # Si la suppression est toujours en cours à la fin du fichier, écrire une nouvelle ligne vide
            if suppression_en_cours:
                fichier.write('\n')

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")


def delete_internal_zones(target_directory):
    try:
        fichier_named_conf = os.path.join(target_directory, "named.conf")
        with open(fichier_named_conf, 'r') as fichier:
            lignes = fichier.readlines()

        with open(fichier_named_conf, 'w') as fichier:
            suppression_en_cours = False  # Variable pour indiquer si la suppression est en cours
            compteur_occurrences = 0  # Compteur d'occurrences de "};"
            
            for i, ligne in enumerate(lignes):
                # Si on trouve le début de la partie à supprimer, activer la suppression
                if 'zone "my.internal.zone" {' in ligne:
                    suppression_en_cours = True

                # Si on trouve la fin de la partie à supprimer, incrémenter le compteur
                elif '};' in ligne and suppression_en_cours:
                    compteur_occurrences += 1

                    # Si on atteint la troisième occurrence, désactiver la suppression
                    if compteur_occurrences == 4:
                        suppression_en_cours = False  
                        ligne = ligne.strip()
                        continue     
            

                # Si la suppression n'est pas en cours, écrire la ligne dans le fichier
                if not suppression_en_cours:
                    fichier.write(ligne)

            # Si la suppression est toujours en cours à la fin du fichier, écrire une nouvelle ligne vide
            if suppression_en_cours:
                fichier.write('\n')

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")


def comment_ddns_key(target_directory):
    try:
        fichier_named_conf = os.path.join(target_directory, "named.conf")
        with open(fichier_named_conf, 'r') as fichier:
            lignes = fichier.readlines()

        with open(fichier_named_conf, 'w') as fichier:
            commentaire_en_cours = False

            for ligne in lignes:
                # Commencer le commentaire si la ligne contient le début du bloc à commenter
                if 'key ddns_key' in ligne and ';' not in ligne:
                    commentaire_en_cours = True

                # Terminer le commentaire si la ligne contient la fin du bloc à commenter
                elif '};' in ligne and commentaire_en_cours:
                    commentaire_en_cours = False
                    ligne = '//' + ligne

                # Ajouter le commentaire ('//' en début de ligne) si le commentaire est en cours
                if commentaire_en_cours:
                    ligne = '//' + ligne

                # Écrire la ligne dans le fichier
                fichier.write(ligne)

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

def delete_external_zones(target_directory):
    try:
        fichier_named_conf = os.path.join(target_directory, "named.conf")
        with open(fichier_named_conf, 'r') as fichier:
            lignes = fichier.readlines()

        with open(fichier_named_conf, 'w') as fichier:
            suppression_en_cours = False  # Variable pour indiquer si la suppression est en cours
            compteur_occurrences = 0  # Compteur d'occurrences de "};"
            
            for i, ligne in enumerate(lignes):
                # Si on trouve le début de la partie à supprimer, activer la suppression
                if 'zone "my.external.zone"' in ligne:
                    suppression_en_cours = True

                # Si on trouve la fin de la partie à supprimer, incrémenter le compteur
                elif '};' in ligne and suppression_en_cours:
                    compteur_occurrences += 1

                    # Si on atteint la troisième occurrence, désactiver la suppression
                    if compteur_occurrences == 1:
                        suppression_en_cours = False  
                        ligne = ligne.strip()
                        continue     
            

                # Si la suppression n'est pas en cours, écrire la ligne dans le fichier
                if not suppression_en_cours:
                    fichier.write(ligne)

            # Si la suppression est toujours en cours à la fin du fichier, écrire une nouvelle ligne vide
            if suppression_en_cours:
                fichier.write('\n')

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")


def action_option2():
    try:
        # Demander à l'utilisateur la version
        version = input("Entrez la version : ")

        # Demander à l'utilisateur les adresses des forwarders séparées par une virgule
        forwarders = input("Entrez les adresses des forwarders (ex : 156.154.70.3,156.154.70.3) '\033[92mséparées par une virgule\033[0m': ")

        # Ajouter les informations dans le fichier
        fichier_named_conf = os.path.join("/var/named/chroot/etc/", "named.conf")
        with open(fichier_named_conf, 'r') as fichier:
            lignes = fichier.readlines()

        with open(fichier_named_conf, 'w') as fichier:
            for ligne in lignes:
                fichier.write(ligne)
                if 'managed-keys-directory "/var/named/dynamic";' in ligne:
                    fichier.write('\n')
                    fichier.write('\tversion "' + version + '";\n')
                    fichier.write('\n')
                    fichier.write('\tforwarders {\n')
                    forwarders_list = forwarders.split(',')
                    for forwarder in forwarders_list:
                        fichier.write('\t\t' + forwarder.strip() + ';\n')
                    fichier.write('\t};\n')

        print(f"Les forwarders ont été ajoutées avec succès dans {fichier_named_conf}.")

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")


def run_command(command):
    subprocess.run(command, shell=True, check=True)

def action_option3():
    # Se déplacer dans le répertoire spécifié
    os.chdir('/var/named/chroot/var/named/')

    # Copier les fichiers depuis /usr/share/doc/bind/sample/var/named/
    run_command('cp -a /usr/share/doc/bind/sample/var/named/* ./')

    # Créer le répertoire 'dynamic'
    run_command('mkdir dynamic')

    # Changer le propriétaire du répertoire
    run_command('chown -R named.named *')

    # Supprimer les fichiers commençant par 'my.' dans le répertoire principal
    run_command('rm my.*')

    # Supprimer les fichiers commençant par 'my.' dans le sous-répertoire 'slaves'
    run_command('rm slaves/my.*')

    restart_named_chroot_service()
    print("Configuration de l'environnement réalisée avec succès.")

def action_option4():
    try:
        # Demande le nom de la vue
        vue_name = input("Entrez le nom de la zone interne : ")

        # Demande le nom du fichier de la vue
        vue_file = input("Entrez le nom du fichier de la zone interne : ")

        # Se déplacer dans le répertoire spécifié
        os.chdir('/var/named/chroot/var/named/')

        # Ouvrir le fichier named.conf en mode lecture
        fichier_named_conf = os.path.join('/var/named/chroot/etc/', "named.conf")
        with open(fichier_named_conf, 'r') as fichier:
            lignes = fichier.readlines()

        # Trouver la ligne avec 'view "internal"'
        index_view_internal = -1
        for i, ligne in enumerate(lignes):
            if 'view "internal"' in ligne:
                index_view_internal = i
                break

        # Vérifier si la ligne 'view "internal"' a été trouvée
        if index_view_internal != -1:
            # Trouver l'index de la 12ème ligne après 'view "internal"'
            index_after_18_lines = index_view_internal + 18

            # Ouvrir le fichier named.conf en mode écriture
            with open(fichier_named_conf, 'w') as fichier:
                # Écrire les lignes originales jusqu'à la ligne 'view "internal"'
                fichier.writelines(lignes[:index_view_internal + 1])

                # Vérifier si l'index après 12 lignes est valide
                if index_after_18_lines < len(lignes):
                    # Écrire les 12 lignes après la ligne 'view "internal"'
                    fichier.writelines(lignes[index_view_internal + 1 : index_after_18_lines + 1])

                    # Écrire la nouvelle zone après les 12 lignes
                    fichier.write(f'\tzone "{vue_name}" {{\n')
                    fichier.write('\t\ttype master;\n')
                    fichier.write(f'\t\tfile "{vue_file}";\n')
                    fichier.write('\t\tallow-update { none; };\n')
                    fichier.write('\t\tallow-transfer { none; };\n')
                    fichier.write('\t};\n')

                    # Écrire le reste des lignes originales après la ligne 'view "internal"'
                    fichier.writelines(lignes[index_after_18_lines + 1 :])

                    print(f"La nouvelle zone a été ajoutée avec succès dans le fichier named.conf.")
                else:
                    print("L'index après 12 lignes dépasse la fin du fichier named.conf.")
        else:
            print("La ligne 'view \"internal\"' n'a pas été trouvée dans le fichier named.conf.")
        
        # Se rendre dans /var/named/chroot/var/named/ et créer le fichier avec le nom spécifié
        os.chdir('/var/named/chroot/var/named/')
        with open(f'{vue_file}', 'w') as zone_file:
            zone_file.write(f'$TTL 86400\n')
            zone_file.write(f'@\tIN\tSOA\tns.{vue_name}.\troot.ns.{vue_name}.\t(\n')
            zone_file.write(f'\t\t\t2024012201 ; Serial\n')
            zone_file.write(f'\t\t\t28800; Refresh\n')
            zone_file.write(f'\t\t\t14400; Retry\n')
            zone_file.write(f'\t\t\t3600000; Expire\n')
            zone_file.write(f'\t\t\t3600; Minimum TTL\n')
            zone_file.write(')\n\n')

            zone_file.write(f'; NAME SERVER IN NS RECORD\n')
            zone_file.write(f'\tIN\tNS\tns.{vue_name}.\n\n')

            zone_file.write('; Records\n')
            #zone_file.write(f'@\tIN\tA\t192.168.190.115\n')
            zone_file.write(f'ns\tIN\tA\t192.168.190.115\n')
            zone_file.write(f'gate\tIN\tA\t192.168.190.2\n')
            zone_file.write(f'pfsense\tIN\tCNAME\tgate\n')

        change_directory_and_chown("/var/named/chroot/var/named/")
        restart_named_chroot_service()

        print(f"{GREEN}Le fichier a été créé avec succès : /var/named/chroot/var/named/{vue_file}.{RESET}")
        print(f"{RED}N'oubliez pas de changer les adresses pour ns gate !{RESET}")
        print(f"{RED}N'oubliez pas de redémarrer le service après avoir ajouté vos entrées !{RESET}")
        print(f"{RED}N'oubliez pas de mettre le DNS dans NMTUI !{RESET}")
      

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")


def action_option5():
    try:
        # Demande le nom de la vue
        vue_name = input("Entrez le nom de la zone externe : ")

        # Demande le nom du fichier de la vue
        vue_file = input("Entrez le nom du fichier de la zone externe : ")

        # Se déplacer dans le répertoire spécifié
        os.chdir('/var/named/chroot/var/named/')

        # Ouvrir le fichier named.conf en mode lecture
        fichier_named_conf = os.path.join('/var/named/chroot/etc/', "named.conf")
        with open(fichier_named_conf, 'r') as fichier:
            lignes = fichier.readlines()

        # Trouver la ligne avec 'view "internal"'
        index_view_external = -1
        for i, ligne in enumerate(lignes):
            if 'view "external"' in ligne:
                index_view_external = i
                break

        # Vérifier si la ligne 'view "internal"' a été trouvée
        if index_view_external != -1:
            # Trouver l'index de la 12ème ligne après 'view "internal"'
            index_after_12_lines = index_view_external + 14

            # Ouvrir le fichier named.conf en mode écriture
            with open(fichier_named_conf, 'w') as fichier:
                # Écrire les lignes originales jusqu'à la ligne 'view "internal"'
                fichier.writelines(lignes[:index_view_external + 1])

                # Vérifier si l'index après 12 lignes est valide
                if index_after_12_lines < len(lignes):
                    # Écrire les 12 lignes après la ligne 'view "internal"'
                    fichier.writelines(lignes[index_view_external + 1 : index_after_12_lines + 1])

                    # Écrire la nouvelle zone après les 12 lignes
                    fichier.write(f'\tzone "{vue_name}" {{\n')
                    fichier.write('\t\ttype master;\n')
                    fichier.write(f'\t\tfile "{vue_file}";\n')
                    fichier.write('\t};\n')

                    # Écrire le reste des lignes originales après la ligne 'view "internal"'
                    fichier.writelines(lignes[index_after_12_lines + 1 :])

                    print(f"La nouvelle zone a été ajoutée avec succès dans le fichier named.conf.")
                else:
                    print("L'index après 12 lignes dépasse la fin du fichier named.conf.")
        else:
            print("La ligne 'view \"external\"' n'a pas été trouvée dans le fichier named.conf.")
        
        # Se rendre dans /var/named/chroot/var/named/ et créer le fichier avec le nom spécifié
        os.chdir('/var/named/chroot/var/named/')
        with open(f'{vue_file}', 'w') as zone_file:
            zone_file.write(f'$TTL 86400\n')
            zone_file.write(f'@\tIN\tSOA\tgate.{vue_name}.\troot.gate.{vue_name}.\t(\n')
            zone_file.write(f'\t\t\t2024012201 ; Serial\n')
            zone_file.write(f'\t\t\t28800; Refresh\n')
            zone_file.write(f'\t\t\t14400; Retry\n')
            zone_file.write(f'\t\t\t3600000; Expire\n')
            zone_file.write(f'\t\t\t3600; Minimum TTL\n')
            zone_file.write(')\n\n')

            zone_file.write(f'; NAME SERVER IN NS RECORD\n')
            zone_file.write(f'\tIN\tNS\tgate.{vue_name}.\n\n')

            zone_file.write('; Record\n')
            zone_file.write(f'ns\tIN\tCNAME\tgate\n')
            zone_file.write(f'gate\tIN\tA\t192.168.254.128\n')
            zone_file.write(f'pfsense\tIN\tCNAME\tgate\n')

        change_directory_and_chown("/var/named/chroot/var/named/")
        restart_named_chroot_service()
        print(f"Le fichier {vue_file} a été créé avec succès dans /var/named/chroot/var/named/.")

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

def action_option6():
    try:
        # Demander le nom de domaine
        nom_domaine = input("Entrez le nom de domaine que vous couvrez (exemple nomDeFamille.swilabus.com) : ")

        # Demander l'adresse IP et la transformer en nom de zone inverse
        adresse_ip = input("Entrez l'adresse IP principale de votre machine routeur: ")
        octets_ip = adresse_ip.split('.')
        nom_zone_inverse = f"{octets_ip[2]}.{octets_ip[1]}.{octets_ip[0]}.in-addr.arpa"

        # Nom du fichier de la zone inverse
        fichier_zone_inverse = f"db.{octets_ip[2]}.{octets_ip[1]}.{octets_ip[0]}"

        # Modifier le fichier named.conf
        os.chdir('/var/named/chroot/etc/')
        with open('named.conf', 'r') as fichier:
            lignes = fichier.readlines()

        # Trouver la vue 'internal' et la section pour insertion
        index_view_internal, index_insertion = -1, -1
        for i, ligne in enumerate(lignes):
            if 'view "internal"' in ligne:
                index_view_internal = i
            if index_view_internal != -1 and "// These are your" in ligne:
                index_insertion = i
                break

        # Vérifier si la vue interne et la position d'insertion sont trouvées
        if index_insertion != -1:
            with open('named.conf', 'w') as fichier:
                fichier.writelines(lignes[:index_insertion])
                fichier.write(f'\tzone "{nom_zone_inverse}" {{\n')
                fichier.write(f'\t\ttype master;\n')
                fichier.write(f'\t\tfile "{fichier_zone_inverse}";\n')
                fichier.write(f'\t\tallow-update {{ none; }};\n')
                fichier.write(f'\t\tallow-transfer {{ none; }};\n')
                fichier.write(f'\t}};\n\n')
                fichier.writelines(lignes[index_insertion:])

            print(f"La zone inverse {nom_zone_inverse} a été ajoutée avec succès dans la vue 'internal'.")

            # Créer le fichier de la zone inverse
            os.chdir('/var/named/chroot/var/named/')
            with open(fichier_zone_inverse, 'w') as zone_file:
                zone_file.write(f'$TTL 86400\n')
                zone_file.write(f'@\tIN\tSOA\tns.{nom_domaine}.\troot.ns.{nom_domaine}. (\n')
                zone_file.write(f'\t\t\t2024010201 ; Serial\n')
                zone_file.write(f'\t\t\t28800 ; Refresh\n')
                zone_file.write(f'\t\t\t14400 ; Retry\n')
                zone_file.write(f'\t\t\t3600000 ; Expire\n')
                zone_file.write(f'\t\t\t3600 ) ; Name error\n\n')

                zone_file.write(f'; NAME SERVER IN NS RECORD\n')
                zone_file.write(f'\tIN\tNS\tns.{nom_domaine}.\n\n')

                # Enregistrements PTR avec le nom de domaine
                zone_file.write(f'1\tIN\tPTR\twindows.{nom_domaine}.\n')
                zone_file.write(f'2\tIN\tPTR\tpfsense.{nom_domaine}.\n')
                zone_file.write(f'115\tIN\tPTR\trouter.{nom_domaine}.\n')

            print(f"Le fichier de la zone inverse {fichier_zone_inverse} a été créé.")
            change_directory_and_chown("/var/named/chroot/var/named/")
            restart_named_chroot_service()
        else:
            print("L'emplacement pour l'insertion de la nouvelle zone n'a pas été trouvé dans named.conf.")

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")


def change_directory_and_chown(directory_path):
    try:
        # Se déplacer dans le répertoire spécifié
        os.chdir(directory_path)

        # Changer le propriétaire du répertoire
        os.system('chown named.named *')

        print(f"Changement de répertoire et de propriétaire effectué avec succès dans {directory_path}.")

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")


def restart_named_chroot_service():
    try:
        # Vérifier si le service est actif
        status_process = subprocess.run(['systemctl', 'is-active', 'named-chroot'], capture_output=True, text=True)
        status = status_process.stdout.strip()

        if status == 'active':
            # Si le service est actif, le redémarrer
            subprocess.run(['systemctl', 'restart', 'named-chroot'])
            print("\033[92mLe service named-chroot a été redémarré.\033[0m")
        else:
            # Si le service n'est pas actif, l'activer et le démarrer
            subprocess.run(['systemctl', 'enable', '--now', 'named-chroot'])
            print("\033[92mLe service named-chroot a été activé et démarré.\033[0m")

    except Exception as e:
        print(f"Une erreur s'est produite : {e}")


def choix_utilisateur():
    try:
        choix = int(input("Choisissez une option (1-7): "))
        print()  # Ajoute une ligne vide
        return choix
    except ValueError:
        print("Veuillez entrer un nombre valide.")
        return None

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
                print("Option invalide. Veuillez choisir une option de 1 à 5.")

if __name__ == "__main__":
    main()