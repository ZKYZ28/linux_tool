#!/usr/bin/python3.9

import os
import subprocess

CYAN = '\033[36m'
RESET = '\033[0m'

def afficher_menu():
    print(f"{CYAN}Menu Quotas :{RESET}")
    print("1. Activer les partitions sur le répertoire /home")
    print("2. Activer un quota pour un utilsateur (login)")
    print("3. Activer un quota pour un groupe")
    print("4. Activer un quota pour un projet")
    print("5. Activer un quota depuis un script")
    print("6. Vérifier l'ensemble de vos quotas")
    print("7. Supprimer quota (utilisateur/groupe/projet)")
    print("8. Quitter")

def choix_utilisateur():
    try:
        return int(input("Entrez votre choix : "))
    except ValueError:
        print("Veuillez entrer un nombre valide.")
        return None
    
def verifier_repertoire():
    current_directory = os.getcwd()
    # Vérifier pour le répertoire courant
    if "/home" in current_directory:
        print("\033[91mAttention : le script est exécuté depuis /home. Veuillez le lancer depuis un autre répertoire pour éviter des erreurs.\033[0m\n")
        return False
    # Vérifier si /home est occupé dans d'autres terminaux
    if subprocess.run("lsof +f -- /home", shell=True).returncode == 0:
        print("\033[91mLe répertoire /home est utilisé. Veuillez quitter le répertoire /home dans tous vos terminaux.\033[0m\n")
        return False
    return True
    
    

def action_option1():
    # Vérifier qu'on n'est dans /home pour ne pas perturber les opérations de unmount et mount
    if not verifier_repertoire():
        return

    # Lire le fichier de configuration pour vérifier si les quotas sont déjà activés
    with open("/etc/fstab", "r") as file:
        if any("grpquota" in line and "usrquota" in line and "prjquota" in line and "/home" in line for line in file):
            print("\033[93mLes quotas sont déjà activés pour /home.\033[0m\n")
            return
        
    # Modifier le fichier de configuration (#r+ permet de lire depuis le début de fichier puis d'écrire)
    with open("/etc/fstab", "r+") as file:
        lines = file.readlines()
        file.seek(0)
        for line in lines:
            if "/home" in line and "xfs" in line and "defaults" in line:
                line = line.replace("defaults", "defaults,grpquota,usrquota,prjquota")
            file.write(line)


    # Recharger les daemons
    subprocess.run("systemctl daemon-reload", shell=True)
    # Démonter /home
    if subprocess.run("umount /home", shell=True).returncode != 0:
        print("Erreur lors du démontage de /home.")
        return
     # Remonter /home
    subprocess.run("mount /home", stdout=subprocess.PIPE, shell=True)

    # Vérifier l'activation
    result = subprocess.run("mount | grep home", stdout=subprocess.PIPE, shell=True)
    output = result.stdout.decode()

    print(output)

    if "grpquota" and "usrquota" and "prjquota" in output:
        print("\033[92mVos quotas sont bien activés : usrquota,prjquota,grpquota présents dans la ligne ci-dessus \033[0m")
    else:
        print("Vos quotas ne sont pas activés. Erreur survenue dans l'exécution. Merci de vérifier votre fichier dans /etc/fstab")

    print()

def verifier_existence_utilisateur(login):
    result = subprocess.run(f"id {login}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"\033[91mL'utilisateur '{login}' n'existe pas sur le système.\033[0m\n")
        return False
    return True

def action_option2():
    login = input("Entrez le nom de l'utilisateur pour le quota : ")
    # Vérifier si l'utilisateur existe
    if not verifier_existence_utilisateur(login):
        return
    
    bsoft = input("Entrez la limite soft du quota en Mo (exemple: 100 pour 100 Mo) : ")
    bhard = input("Entrez la limite hard du quota en Mo (exemple: 150 pour 150 Mo) : ")

    quota_command = f"xfs_quota -x -c 'limit bsoft={bsoft}m bhard={bhard}m {login}' /home"
    subprocess.run(quota_command, shell=True)

    # Afficher le rapport des quotas pour l'utilisateur
    report_user_quota_command = f"xfs_quota -x -c 'report -u -a -h' /home | grep {login}"
    result = subprocess.run(report_user_quota_command, shell=True, stdout=subprocess.PIPE)
    report_output = result.stdout.decode()
    
    # Afficher l'en-tête et le rapport pour l'utilisateur
    print()
    print("\033[93mVoici le quota appliqué :\033[0m")
    print("User ID      Used   Soft   Hard Warn/Grace")
    print("---------- ---------------------------------")
    print(report_output)

    if result.returncode != 0:
        print(f"\033[91mUne erreur s'est produite lors de la récupération du rapport de quota pour l'utilisateur ${login}.\033[0m")

def verifier_existence_groupe(groupName):
    result = subprocess.run(f"getent group {groupName}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"\033[91mLe groupe '{groupName}' n'existe pas sur le système.\033[0m\n")
        return False
    return True

def action_option3():
    groupName = input("Entrez le nom du groupe pour le quota : ")
    if not verifier_existence_groupe(groupName):
        return
    
    bsoft = input("Entrez la limite soft du quota en Mo (exemple: 100 pour 100 Mo) : ")
    bhard = input("Entrez la limite hard du quota en Mo (exemple: 150 pour 150 Mo) : ")

    quota_command = f"xfs_quota -x -c 'limit -g bsoft={bsoft}m bhard={bhard}m {groupName}' /home"
    subprocess.run(quota_command, shell=True)

     # Afficher le rapport des quotas pour le groupe
    report_group_quota_command = f"xfs_quota -x -c 'report -g -a -h' /home | grep {groupName}"
    result = subprocess.run(report_group_quota_command, shell=True, stdout=subprocess.PIPE)
    report_output = result.stdout.decode()
    
    # Afficher l'en-tête et le rapport pour le groupe
    print()
    print("\033[93mVoici le quota appliqué :\033[0m")
    print("Group ID     Used   Soft   Hard Warn/Grace")
    print("---------- ---------------------------------")
    print(report_output)

    if result.returncode != 0:
        print(f"\033[91mUne erreur s'est produite lors de la récupération du rapport de quota pour le groupe ${groupName}.\033[0m")

def creer_dossier_projet(nom_projet):
    dossier_projet = f"/home/{nom_projet}"
    if not os.path.exists(dossier_projet):
        os.makedirs(dossier_projet)
        print(f"\nDossier pour le projet '{nom_projet}' créé dans /home. Chemin final est '/home/{nom_projet}'")
    else:
        print(f"\nLe dossier pour le projet '{nom_projet}' existe déjà.")

def mettre_a_jour_fichiers_projet(id_projet, nom_projet):
    with open("/etc/projects", "a") as proj_file:
        proj_file.write(f"{id_projet}:/home/{nom_projet}\n")

    with open("/etc/projid", "a") as projid_file:
        projid_file.write(f"{nom_projet}:{id_projet}\n")


def definir_quota_projet(nom_projet, bsoft, bhard):
    subprocess.run(f"xfs_quota -x -c 'project -s {nom_projet}' /home", shell=True)
    print("\033[92mSetting up ... depth infine(-1) apparait ci-dessus ? T'es sur la bonne voie.\033[0m")
    subprocess.run(f"xfs_quota -x -c 'limit -p bsoft={bsoft}m bhard={bhard}m {nom_projet}' /home", shell=True)
    print(f"\033[92mQuota pour le projet '{nom_projet}' défini avec succès.\033[0m")

def action_option4():
    nom_projet = input("Entrez le nom du projet : ")
    id_projet = input("Entrez l'ID numérique du projet : ")
    bsoft = input("Entrez la limite soft du quota en Mo (exemple: 100 pour 100 Mo) : ")
    bhard = input("Entrez la limite hard du quota en Mo (exemple: 150 pour 150 Mo) : ")

    creer_dossier_projet(nom_projet)
    mettre_a_jour_fichiers_projet(id_projet, nom_projet)
    definir_quota_projet(nom_projet, bsoft, bhard)

    # Afficher le rapport des quotas pour le projet
    report_group_quota_command = f"xfs_quota -x -c 'report -p -a -h' /home | grep {nom_projet}"
    result = subprocess.run(report_group_quota_command, shell=True, stdout=subprocess.PIPE)
    report_output = result.stdout.decode()
    
    # Afficher l'en-tête et le rapport pour le groupe
    print()
    print("\033[93mVoici le quota appliqué :\033[0m")
    print("Project ID   Used   Soft   Hard Warn/Grace")
    print("---------- ---------------------------------")
    print(report_output)

    if result.returncode != 0:
        print(f"\033[91mUne erreur s'est produite lors de la récupération du rapport de quota pour le projet ${nom_projet}.\033[0m")



def action_option5():
    # Lancer le script Python depuis le répertoire Documents
    script_add_quota = '/root/Documents/createQuotaByServices.py'  # Remplacez par le chemin complet de votre script
    try:
        subprocess.run(["python3.9", script_add_quota], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Une erreur s'est produite lors de l'exécution du script Python $ {script_add_quota}: {e}")
    except Exception as e:
        print(f"Erreur générale dans le script ${script_add_quota} : {e}")


def action_option6():
    subprocess.run(f"xfs_quota -x -c 'report -a -h' /home", shell=True)

def supprimer_ligne_fichier(chemin_fichier, motif_exact):
    with open(chemin_fichier, "r") as file:
        lignes = file.readlines()
    with open(chemin_fichier, "w") as file:
        for ligne in lignes:
            if ligne.strip() != motif_exact:
                file.write(ligne)

def supprimer_quota_utilisateur(user_name):
    subprocess.run(f"xfs_quota -x -c 'limit bsoft=0 bhard=0 {user_name}' /home", shell=True)
    print(f"\033[92mQuota de l'utilisateur '{user_name}' supprimé.\033[0m\n\n")

def supprimer_quota_groupe(group_name):
    subprocess.run(f"xfs_quota -x -c 'limit -g bsoft=0 bhard=0 {group_name}' /home", shell=True)
    print(f"\033[92mQuota du groupe '{group_name}' supprimé.\033[0m\n\n")

def action_option7():
    choix = input("Voulez-vous supprimer un quota pour un utilisateur (u), un groupe (g), ou un projet (p), vide pour annuler ? [u/g/p] : ")
    if choix == 'u':
        user_name = input("Entrez le nom de l'utilisateur dont le quota doit être supprimé : ")
        supprimer_quota_utilisateur(user_name)
    elif choix == 'g':
        group_name = input("Entrez le nom du groupe dont le quota doit être supprimé : ")
        supprimer_quota_groupe(group_name)
    elif choix == 'p':
        # Suppression d'un projet
        nom_projet = input("Entrez le nom associé au projet à supprimer ($ vim /etc/projid pour vérifier) : ")
        id_projet = input("Entrez l'id numérique associé au projet à supprimer ($ vim /etc/projid pour vérifier) : ")
        subprocess.run(f"xfs_quota -x -c 'limit -p bsoft=0 bhard=0 {nom_projet}' /home", shell=True)
        subprocess.run(f"xfs_quota -x -c 'project -C {nom_projet}' /home", shell=True)
        supprimer_ligne_fichier("/etc/projects", f"{id_projet}:/home/{nom_projet}")
        supprimer_ligne_fichier("/etc/projid", f"{nom_projet}:{id_projet}")
        print(f"\033[92mProjet '{nom_projet}' supprimé avec succès\033[0m. \033[93mLe dossier du projet est à supprimer manuellement !\033[0m\n")
    else:
        return


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
                print("Option invalide. Veuillez choisir une option de 1 à 7.")

if __name__ == "__main__":
    main()