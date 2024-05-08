#!/usr/bin/python3.9

import subprocess

ascii_art = r'''      
--------------------------------------------                                  
 ____                                    
|    \ ___ ___ ___ _ _ ___ ___   ___ _ _ 
|  |  | . |   | . | | | .'|   |_| . | | |
|____/|___|_|_|___|\_/|__,|_|_|_|  _|_  |
                                |_| |___|

-------------------------------------------- 
'''

# Couleurs ANSI
BLACK = '\033[30m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
BROWN = '\033[38;5;94m'
PINK = '\033[38;5;206m'
RESET = '\033[0m'


def afficher_menu(): 
    print(ascii_art)
    print(f"{WHITE}1. Apache{RESET}")
    print(f"{BLUE}2. FTP{RESET}")
    print(f"{YELLOW}3. DNS{RESET}")
    print(f"{GREEN}4. Backup{RESET}")
    print(f"{CYAN}5. Quotas{RESET}")
    print(f"{MAGENTA}6. MAIL{RESET}")
    print(f"{BROWN}7. FireWall{RESET}")
    print(f"{PINK}8. DHCP{RESET}")
    print(f"{RED}9. Quitter{RESET}")


def apache_luncher():
    try:
        subprocess.run(["python3.9", "/root/Documents/SCRIPTS/APACHE/apacheConfigurator.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution du script Apache : {e}")

def ftp_luncher():
    try:
        subprocess.run(["python3.9", "/root/Documents/SCRIPTS/FTP/ftpConfigurator.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution du script FTP : {e}")

def dns_luncher():
    try:
        subprocess.run(["python3.9", "/root/Documents/SCRIPTS/DNS/dnsConfigurator.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution du script DNS : {e}")

def backup_luncher():
    try:
        subprocess.run(["python3.9", "/root/Documents/SCRIPTS/BACKUP/backupConfigurator.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution du script Backup : {e}")

def quotas_luncher():
    try:
        subprocess.run(["python3.9", "/root/Documents/SCRIPTS/OTHER/QUOTA/quotaConfigurator.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution du script Quotas : {e}")

def mail_luncher():
    try:
        subprocess.run(["python3.9", "/root/Documents/SCRIPTS/OTHER/MAIL/mailConfigurator.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution du script Mail : {e}")

def firewall_luncher():
    try:
        subprocess.run(["python3.9", "/root/Documents/SCRIPTS/OTHER/FIREWALL/firewallConfigurator.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution du script Mail : {e}")

def dhcp_luncher():
    try:
        subprocess.run(["python3.9", "/root/Documents/SCRIPTS/OTHER/DHCP/dhcpConfigurator.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution du script DHCP : {e}")

def choix_utilisateur():
    try:
        choix = int(input("Choisissez une option (1-9): "))
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
                apache_luncher()
            elif choix == 2:
                ftp_luncher()
            elif choix == 3:
                dns_luncher()
            elif choix == 4:
                backup_luncher()
            elif choix == 5:
                quotas_luncher()
            elif choix == 6:
                mail_luncher()
            elif choix == 7:
                firewall_luncher()
            elif choix == 8:
                dhcp_luncher()
            elif choix == 9:
                print("Donovan.py arrêté avec succès.")
                break
            else:
                print("Option invalide. Veuillez choisir une option de 1 à 9.")

if __name__ == "__main__":
    main()