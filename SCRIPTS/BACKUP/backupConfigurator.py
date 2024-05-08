#!/usr/bin/python3.9

import subprocess
import tempfile

GREEN = '\033[32m'
RESET = '\033[0m'

def afficher_menu():
    print()
    print(f"{GREEN}Menu Backup : {RESET}")
    print("1. PLanifier une backup")
    print("2. Vérifier les tâches planifiées")
    print("3. Supprimer les tâches planifiées")
    print("4. Quitter")

def action_option1():
    commande_compress = input("Entrez la commande pour créer l'archive : ")
    commande_sender = input("Entrez la commande pour envoyer l'archive : ")

    # Demander à l'utilisateur les détails pour la planification de la backup
    print("\n--- Partie crontab ---")
    print("Utilisez * si vous voulez toutes les valeurs !")
    minutes = input("Minutes : ")
    heure = input("Heure : ")
    jour_mois = input("Jour du mois : ")
    mois = input("Mois : ")
    jours_semaine = input("Jours de la semaine (séparés par des espaces) : ")

    # Remplacer les espaces par des virgules dans jours_semaine
    jours_semaine = jours_semaine.replace(" ", ",")


    # Construire la commande crontab
    crontab_commande_compress= f"{minutes} {heure} {jour_mois} {mois} {jours_semaine} {commande_compress}"
    crontab_commande_sender = f"{minutes} {heure} {jour_mois} {mois} {jours_semaine} {commande_sender}"

    planifier_backup(crontab_commande_compress, crontab_commande_sender)

    print("Tâche planifiée avec succès.")

def planifier_backup(crontab_commande_compress, crontab_commande_sender):
    # Créer un fichier temporaire avec le contenu de crontab_commande
    crontab_content = f"{crontab_commande_compress}\n{crontab_commande_sender}\n"
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        temp_file.write(crontab_content)
    

    # Utiliser la commande crontab pour charger le fichier temporaire
    subprocess.run(["crontab", temp_file.name])

    # Supprimer le fichier temporaire après avoir chargé le crontab
    temp_file.close()
    # Supprimer le fichier temporaire
    subprocess.run(["rm", temp_file.name])


def action_option2():
    # Exécuter la commande crontab -l
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    
    # Afficher le résultat
    crontab_content = result.stdout.strip()  # Supprimer les espaces vides autour de la sortie
    
    if crontab_content:
        print(crontab_content)
    else:
        print("Aucune tâche planifiée.")



def action_option3():
    # Demander confirmation à l'utilisateur avant de supprimer tout le crontab
    confirmation = input("Êtes-vous sûr de vouloir supprimer toutes les tâches planifiées ? (yes/no): ").lower()

    if confirmation == "yes":
        # Supprimer tout le crontab
        subprocess.run(["crontab", "-r"], check=True)
        print("Toutes les tâches planifiées ont été supprimées.")
    else:
        print("Suppression du crontab annulée.")

  

def choix_utilisateur():
    try:
        choix = int(input("Choisissez une option (1-4): "))
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
                print("Au revoir!")
                break
            else:
                print("Option invalide. Veuillez choisir une option de 1 à 4.")

if __name__ == "__main__":
    main()