#!/usr/bin/python3.9

SOURCE = "/root/Documents/SCRIPTS/OTHER/USERS/liste-utilisateurs.txt" #Chemin vers le fichier qui contient tous les utilisateurs
SPLIT = ':' #Element séparateur dans le fichier avec tous les utilisateurs


def ajouter_logins_user_list(file_path):
    try:
        # Lire le fichier et extraire les logins
        with open(file_path, 'r') as fichier:
             logins = []
             for ligne in fichier:
                # supprimer le dernière caractère \n afin de traiter que la donnée grâce à rstrip
                # print(f"ligne lue > {ligne.rstrip()}")
                elements = ligne.strip().split(SPLIT)

                if len(elements) == 5:
                    nom, prenom, service, login, motPasse = elements
                    logins.append(login)
                    print(f"{login} ajouté avec succès !")

        # Ajouter les logins à la fin du fichier /etc/vsftpd/user_list
        with open('/etc/vsftpd/user_list', 'a') as user_list_file:
            for login in logins:
                user_list_file.write(login + '\n')

        print(f"Utilisateur(s) ajoutés avec succès au fichier.")
        
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

if __name__ == "__main__":
    ajouter_logins_user_list(SOURCE)