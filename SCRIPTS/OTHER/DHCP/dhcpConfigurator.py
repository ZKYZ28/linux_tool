#!/usr/bin/python3.9
import subprocess

PINK = '\033[38;5;206m'
RESET = '\033[0m'

def afficher_menu():
    print()
    print(f"{PINK}Menu DHCP :{RESET}")
    print("1. Mettre en place la configuration de base de DHCP")
    print("2. Changer facilement le ou les serveurs DNS")
    print("3. Ajouter une réservation (Adresse IP FIXE pour une adresse MAC)")
    print("4. Quitter")
    

def choix_utilisateur():
    try:
        choix = int(input("Choisissez une option (1-4): "))
        print()  # Ajoute une ligne vide
        return choix
    except ValueError:
        print("Veuillez entrer un nombre valide.")
        return None

def action_option1():
    # 1. Copier le fichier de configuration exemple
    subprocess.run('cp /usr/share/doc/dhcp-server/dhcpd.conf.example /etc/dhcp/dhcpd.conf', shell=True)

    # 2. Avez-vous déjà modifié le dhcp ?
    deja_modifie = input("Avez-vous déjà modifié le fichier relatif au DHCP (o/n) : ").lower()
    if deja_modifie == 'o':
        print("\033[91mTu vas écraser ton fichier DHCP alors. Va vérifier avant de l'écraser totalement !\033[0m")
        return

     # Lire le contenu du fichier de configuration
    try:
        with open('/etc/dhcp/dhcpd.conf', 'r') as file:
            config_lines = file.readlines()
    except IOError:
        print("Erreur lors de la lecture du fichier de configuration.")
        return

    # 2. Supprimer les sections inutiles
    start_remove = False
    domain_names = input("Entrez le ou les adresses ip des serveurs DNS (séparés par des virgules) : ")
    domain_name_replaced = False
    domain_line_replaced = False
    cleaned_config = []
    for line in config_lines:
        if "No service" in line:
            start_remove = True
        if "# Fixed IP addresses can also be specified for hosts." in line:
            start_remove = False
        if 'option domain-name-servers' in line and not domain_line_replaced:
            line = f"option domain-name-servers {domain_names};\n"
            domain_line_replaced = True
        if 'option domain-name "example.org";' in line and not domain_name_replaced:
            line = 'option domain-name "localdomain";\n'
            domain_name_replaced = True
        if not start_remove:
            cleaned_config.append(line)


    # 4. Créer une entrée 'shared-network'
    network_name = 'RESEAU-CLIENT'
    subnet_ip = input("Entrez l'adresse IP du sous-réseau (doit se terminer par un .0): ")
    min_ip = input("Entrez l'adresse IP minimale de la range : ")
    max_ip = input("Entrez l'adresse IP maximale de la range: ")
    router_ip = input("Entrez l'adresse IP du routeur (adresse ip de la machine routeur sur le réseau client) : ")
    broadcast_ip = subnet_ip.rsplit('.', 1)[0] + '.255'

    shared_network_config = f"""
shared-network {network_name} {{
    subnet {subnet_ip} netmask 255.255.255.0 {{
        range {min_ip} {max_ip};
        option routers {router_ip};
        option broadcast-address {broadcast_ip};
    }}
}}
"""

    # Ajouter les configurations au fichier
    cleaned_config.append(shared_network_config)

    # 8. Commenter les lignes restantes après la ligne spécifiée
    for index, line in enumerate(cleaned_config):
        if "# Fixed IP addresses can also be specified for hosts." in line:
            cleaned_config = cleaned_config[:index + 1] + ['# ' + l for l in cleaned_config[index + 1:]]

    # Écrire la configuration nettoyée dans le fichier
    with open('/etc/dhcp/dhcpd.conf', 'w') as file:
        file.writelines(cleaned_config)

    print("\033[92mConfiguration du DHCP terminée avec succès. Attention si pas /24 changer le netmask : /etc/dhcp/dhcpd.conf ! \033[0m")
    manage_dhcp_service()

def action_option2():

    deja_modifie = input("Avez-vous déjà configuré le fichier relatif au DHCP (o/n) : ").lower()
    if deja_modifie == 'n':
        print("\033[91mVa d'abord réaliser la configuration de base. (option 1) !\033[0m")
        return

    # Lire le contenu du fichier de configuration
    try:
        with open('/etc/dhcp/dhcpd.conf', 'r') as file:
            config_lines = file.readlines()
    except IOError:
        print("\033[91mErreur lors de la lecture du fichier de configuration.\033[0m")
        return

    # Demander les nouveaux serveurs DNS
    new_dns_servers = input("Entrez le ou les adresses ip des serveurs DNS (séparés par des virgules) : ")

    updated_config = []
    for line in config_lines:
        if 'option domain-name-servers' in line:
            line = f"option domain-name-servers {new_dns_servers};\n"
        updated_config.append(line)

    # Écrire la configuration mise à jour dans le fichier
    try:
        with open('/etc/dhcp/dhcpd.conf', 'w') as file:
            file.writelines(updated_config)
        print("\033[92mLes serveurs DNS ont été mis à jour avec succès.\033[0m")
        print("\033[92mConfiguration du DHCP modifiée avec succès. Vous pouvez vérifier en faisant vim /etc/dhcp/dhcpd.conf\033[0m")
    except IOError:
        print("\033[91mErreur lors de l'écriture du fichier de configuration.\033[0m")
    manage_dhcp_service()


def action_option3():

    deja_modifie = input("Avez-vous déjà configuré le fichier relatif au DHCP (o/n) : ").lower()
    if deja_modifie == 'n':
        print("\033[91mVa d'abord réaliser la configuration de base. (option 1) !\033[0m")
        return
 # Demander l'adresse MAC
    mac_address = input("Entrez l'adresse MAC de la machine cliente (format 00:0c:29:29:ff:bc) : ")

    # Demander l'adresse IP fixe
    fixed_ip = input("Entrez l'adresse IP fixe souhaitée : ")

    # Formater la configuration de réservation
    reservation_config = f"""
host client {{
  hardware ethernet {mac_address};
  fixed-address {fixed_ip};
}}
"""

    # Écrire la configuration de réservation à la fin du fichier
    try:
        with open('/etc/dhcp/dhcpd.conf', 'a') as file:
            file.write(reservation_config)
        print("\033[92mRéservation ajoutée avec succès. Vous pouvez vérifier en faisant vim /etc/dhcp/dhcpd.conf\033[0m")
    except IOError:
        print("\033[91mErreur lors de l'écriture du fichier de configuration.\033[0m")
    manage_dhcp_service()

def manage_dhcp_service():
    try:
        # Vérifier l'état du service DHCP
        status_result = subprocess.run(['systemctl', 'is-active', 'dhcpd'], capture_output=True, text=True)
        if status_result.stdout.strip() == 'active':
            # Redémarrer le service si actif
            subprocess.run(['systemctl', 'restart', 'dhcpd'])
            print("\033[92mService DHCP redémarré avec succès.\033[0m")
        else:
            # Démarrer le service s'il n'est pas actif
            subprocess.run(['systemctl', 'enable', '--now', 'dhcpd'])
            print("\033[92mService DHCP démarré avec succès.\033[0m")
    except subprocess.SubprocessError as e:
        print("\033[91mErreur lors de la gestion du service DHCP: ", e, "\033[0m")

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