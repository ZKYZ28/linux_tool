#!/usr/bin/python3.9

import os
import subprocess

BROWN = '\033[38;5;94m'
RED = '\033[31m'
RESET = '\033[0m'

def afficher_menu():
    print()
    print(f"{BROWN}Menu FireWall :{RESET}")
    print("1. Initialiser le script Routeur")
    print("2. Initialiser le script Client")
    print("3. Rendre actif Firewall")
    print("4. Voir les règles actuelles")
    print("5. Supprimer les règles actuelles")
    print("6. Mettre les règles actuelles par défaut")
    print("7. Ouvir un port sur le Routeur")
    print("8. Ouvir un port sur le Client")
    print("9. Quitter")

def action_option1():
    # Vérifier si le fichier existe déjà
    file_path = "/root/Documents/SCRIPTS/OTHER/FIREWALL/server.nft"

    if not os.path.exists(file_path):
        print("Configuration de base pour le Routeur:")
        
        # Demander à l'utilisateur les informations nécessaires
        ip_interface2_router = input("Adresse IP de l'interface numéro 2 du ROUTEUR : ")
        name_interface2_router = input("Nom de l'interface numéro 2 du ROUTEUR : ")
        ip_interface3_router = input("Adresse IP de l'interface numéro 3 avec la dernière valeur remplacée par 0 : ")
        name_interface3_router = input("Nom de l'interface numéro 3 : ")
        ip_interface2_client = input("Adresse IP de l'interface numéro 2 du CLIENT : ")

        octets = ip_interface2_router.split('.')
        if len(octets) == 4:
            octets[-1] = '0'
            firewall_lan = '.'.join(octets)
        else:
            print("L'adresse IP n'est pas au format attendu.")

        with open(file_path, "w") as file:
            file.write(f"""#!/usr/sbin/nft -f

### DECLARATION
define FIREWALL_LAN ={{{firewall_lan}/24}}
define UNTRUST_IP = {ip_interface2_router}
define UNTRUST_IF = {name_interface2_router}
define TRUST_NET = {{{ip_interface3_router}/24}}
define TRUST_IF = {name_interface3_router}
define CLIENT_IP = {ip_interface2_client}

define PUBLIC_TCP_PORT = {{ 53 }}
define PUBLIC_UDP_PORT = {{ 53 }}

define PORTS_ACCEPT_CLIENT = {{ 80, 443 }}
define FIREWALL_TCP = {{ 53 }}


#FLUSH ALL RULES
flush ruleset

### FIREWALL BASE
table inet MyFirewall{{
    ### FILTRAGE 
    chain firewall_to_untrust{{
        accept
    }}
    
    chain untrust_to_firewall {{
        #Par défaut
        ip daddr $UNTRUST_IP udp dport $PUBLIC_UDP_PORT accept
		ip saddr $FIREWALL_LAN ip protocol icmp accept

        ct state new ip daddr $UNTRUST_IP tcp dport $FIREWALL_TCP accept
        ct state invalid drop 
        ct state established,related accept 
        log 
        drop
    }}

    chain trust_to_firewall {{
        accept
    }}

    chain firewall_to_trust {{
        accept
    }}

    chain trust_to_untrust {{
        #Par défaut
ip saddr $TRUST_NET udp dport $PUBLIC_UDP_PORT accept
ip saddr $TRUST_NET ip protocol icmp accept

        ct state new ip saddr $TRUST_NET tcp dport $PORTS_ACCEPT_CLIENT  accept
		ct state invalid drop
		ct state established, related accept
		log
		drop
    }}

    chain untrust_to_trust{{
        #Par défaut
ip daddr $CLIENT_IP udp dport $PUBLIC_TCP_PORT accept 
        
        ct state new ip daddr $CLIENT_IP tcp dport $PUBLIC_TCP_PORT accept 
ct state invalid drop 
ct state established,related accept 
log 
drop
    }}

    ### REPARTITION
	chain incoming {{
		type filter hook input priority 0; policy drop;

        #Par défaut
		meta iif lo accept
		meta iif $UNTRUST_IF jump untrust_to_firewall
		meta iif $TRUST_IF jump trust_to_firewall
		log
	}}

	chain forwarding {{
		type filter hook forward priority 0; policy drop;

        #Par défaut
		meta iif $UNTRUST_IF meta oif $TRUST_IF jump untrust_to_trust
		meta iif $TRUST_IF  meta oif $UNTRUST_IF  jump trust_to_untrust
		log
	}}

	chain outgoing {{
		type filter hook output priority 0; policy drop;

        #Par défaut
		meta oif lo accept
		meta oif $UNTRUST_IF jump firewall_to_untrust
		meta oif $TRUST_IF jump firewall_to_trust
		log
	}}
}}

### FIREWALL NAT 
table ip MyFirewallNAT {{
    chain nat_in {{
        type nat hook prerouting priority -100;

        #Par défaut
        meta iif $UNTRUST_IF ip daddr $UNTRUST_IP tcp dport $PUBLIC_TCP_PORT dnat to $CLIENT_IP
        meta iif $UNTRUST_IF ip daddr $UNTRUST_IP udp dport $PUBLIC_UDP_PORT dnat to $CLIENT_IP
    }}

    chain nat_out {{
        type nat hook postrouting priority 100;

        #Par défaut
        meta oif $UNTRUST_IF ip saddr $TRUST_NET masquerade
    }}
}}""")
        
        print("Fichier server.nft créé avec succès : /root/Documents/SCRIPTS/OTHER/FIREWALL/server.nft . Attention de changer les /24 si jamais ce n'est pas ça !")
    else:
        print("Le fichier server.nft existe déjà. Aucune modification effectuée.")
        

def action_option2():
    # Vérifier si le fichier existe déjà
    file_path = "/root/Documents/SCRIPTS/OTHER/FIREWALL/client.nft"

    if not os.path.exists(file_path):
        print("Configuration de base pour le Client:")
        
        # Demander à l'utilisateur les informations nécessaires
        lan4_internal = input("Adresse IP Interface numéro 3 avec la dernière valeur remplacée par 0 : ")
        lan6_internal = input("Les 4 première valeur de ce qui a après inet6 dans la 3ème interface : ")

        with open(file_path, "w") as file:
            file.write(f"""#!/usr/sbin/nft -f

### DECLARATION
define LAN4_INTERNAL = {{{lan4_internal}/24}}
define LAN6_INTERNAL = {{{lan6_internal}::/10}}
define PUBLIC_TCP_PORT = {{ 53 }}
define PUBLIC_UDP_PORT = {{ 53 }}

#FLUSH ALL RULES
flush ruleset

### FIREWALL BASE
table inet MyFirewall{{
    ### REPARTITION
    chain incoming {{
       type filter hook input priority 0; policy drop;
		meta iif lo accept
		ct state invalid drop
		ct state established, related accept
		udp dport $PUBLIC_UDP_PORT accept

		ct state new tcp dport $PUBLIC_TCP_PORT accept
		
		### CONNECTION DE BASE
		ip saddr $LAN4_INTERNAL ip protocol icmp accept
		ip6 saddr $LAN6_INTERNAL ip6 nexthdr icmpv6 accept
		log
    }}

    chain forwarding {{
        type filter hook forward priority 0; policy accept;
    }}

    chain outgoing {{
        type filter hook output priority 0; policy accept;
        meta oif lo accept
    }}

}}""")
            
        print("Fichier client.nft créé avec succès : /root/Documents/SCRIPTS/OTHER/FIREWALL/client.nft. Attention de changer le /24 si jamais ce n'est pas ça !")
    else:
        print("Le fichier client.nft existe déjà. Aucune modification effectuée.")


def action_option3():

    # Demander à l'utilisateur s'il veut activer le serveur ou le client
    choix = input("Voulez-vous activer le serveur (s) ou le client (c) ? ")

    if choix.lower() == "s":
        # Exécuter la commande pour activer le serveur
        subprocess.run(["nft", "-f", "/root/Documents/SCRIPTS/OTHER/FIREWALL/server.nft"], check=True)
        print("Le script de Firewall serveur a été activé avec succès.")
    elif choix.lower() == "c":
        # Exécuter la commande pour donner les permissions d'exécution au fichier
        chmod_command = "chmod +x /root/Documents/SCRIPTS/OTHER/FIREWALL/client.nft"
        subprocess.run(chmod_command, shell=True)

        # Exécuter le script de Firewall client
        client_script_path = "/root/Documents/SCRIPTS/OTHER/FIREWALL/client.nft"
        subprocess.run([client_script_path], check=True)
        print("Le script de Firewall client a été activé avec succès.")
    else:
        print("Choix invalide. Veuillez choisir 's' pour serveur ou 'c' pour client.")

def action_option4():
    try:
        result = subprocess.run(["nft", "list", "ruleset"], stdout=subprocess.PIPE, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de 'nft list ruleset': {e}")


def action_option5():
    confirmation = input(f"{RED}Êtes-vous sûr de vouloir supprimer toutes les règles de firewall {RED}(ATTENTION REGLES DOCKER){RESET} ? (yes/no): ").lower()

    if confirmation == 'yes':
        try:
            # Exécuter la commande pour supprimer toutes les règles
            subprocess.run(["nft", "flush", "ruleset"], check=True)
            print("Toutes les règles de firewall ont été supprimées avec succès.")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la suppression des règles de firewall : {e}")
    else:
        print("Suppression des règles annulée.")


def action_option6():
    try:
        
        # Mettre les règles par défaut pour le serveur
        subprocess.run(["nft", "list", "ruleset"], stdout=subprocess.PIPE, text=True, check=True)
        with open("/etc/nftables/default.nft", "w") as file:
            file.write(subprocess.run(["nft", "list", "ruleset"], stdout=subprocess.PIPE, text=True, check=True).stdout)
        print("Les règles par défaut pour le serveur ont été sauvegardées avec succès.")
    
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la sauvegarde des règles par défaut : {e}")
  

def action_option7():
    # Demander s'il s'agit du routeur ou du client
    choix = input("Voulez-vous ouvrir un port pour un service sur le routeur (R) ou le client (C) ? ").lower()

    if choix == 'r':
        # Pour le routeur
        ports = input("Entrez le ou les ports à ouvrir séparés par un espace : ")
        formatted_ports = ', '.join(ports.split())

        # Lire le fichier /root/Documents/server.nft
        with open('/root/Documents/SCRIPTS/OTHER/FIREWALL/server.nft', 'r') as file:
            content = file.read()
        # Rajouter les ports dans le fichier
        content = content.replace("define FIREWALL_TCP = { 53 }", f"define FIREWALL_TCP = {{ 53, {formatted_ports} }}")

        with open('/root/Documents/SCRIPTS/OTHER/FIREWALL/server.nft', 'w') as file:
            file.write(content)

    elif choix == 'c':
        # Pour le client
        ports = input("Entrez le ou les ports à ouvrir séparés par un espace : ")
        formatted_ports = ', '.join(ports.split())

        # Lire le fichier /root/Documents/client.nft
        with open('/root/Documents/SCRIPTS/OTHER/FIREWALL/server.nft', 'r') as file:
            content = file.read()
        # Rajouter les ports dans le fichier
        content = content.replace("define PUBLIC_TCP_PORT = { 53 }", f"define PUBLIC_TCP_PORT = {{ 53, {formatted_ports} }}")

        with open('/root/Documents/SCRIPTS/OTHER/FIREWALL/server.nft', 'w') as file:
            file.write(content)

        # Afficher un message d'avertissement en rouge
        print(RED + "Ne pas oublier d'ouvrir le/les port(s) sur le client !" + RESET)

    else:
        print("Choix invalide.")

def  action_option8():
    ports = input("Entrez le ou les ports à ouvrir séparés par un espace : ")
    formatted_ports = ', '.join(ports.split())

    # Lire le fichier /root/Documents/server.nft
    with open('/root/Documents/SCRIPTS/OTHER/FIREWALL/client.nft', 'r') as file:
        content = file.read()
    # Rajouter les ports dans le fichier
    content = content.replace("define PUBLIC_TCP_PORT = { 53 }", f"define PUBLIC_TCP_PORT = {{ 53, {formatted_ports} }}")

    with open('/root/Documents/SCRIPTS/OTHER/FIREWALL/client.nft', 'w') as file:
        file.write(content)

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
                action_option8()
            elif choix == 9:
                print("Au revoir!")
                break
            else:
                print("Option invalide. Veuillez choisir une option de 1 à 9.")

if __name__ == "__main__":
    main()