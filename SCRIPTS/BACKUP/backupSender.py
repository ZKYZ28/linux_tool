#!/usr/bin/python3.9

import subprocess
import argparse

def compresser_dossier(source, destination, format_archive):
    try:
        if format_archive == 'zip':
            subprocess.run(['zip', '-r', destination, source], check=True)
        elif format_archive == 'tar.gz':
            subprocess.run(['tar', 'czf', destination, source], check=True)
        elif format_archive == 'tar.bz2':
            subprocess.run(['tar', 'cjf', destination, source], check=True)
        elif format_archive == 'tar.xz':
            subprocess.run(['tar', 'cJf', destination, source], check=True)
        else:
            print("Format d'archive non pris en charge.")
            return

        print(f"Archive créée avec succès : {destination}")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution des commandes : {e}")


def executer_commande(commande):
    try:
        subprocess.run(commande, shell=True, check=True)
        print('La commande a été exécutée avec succès.')
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande : {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script de compression et transfert FTP')
    parser.add_argument('--source', required=True, help='Chemin du dossier source à compresser')
    parser.add_argument('--destination', required=True, help='Chemin de l\'archive compressée')
    parser.add_argument('--format', required=True, choices=['zip', 'tar.gz', 'tar.bz2', 'tar.xz'], help='Format de l\'archive')
    parser.add_argument('--command', required=True, help='Commande lftp complète pour le transfert FTP')

    args = parser.parse_args()

    compresser_dossier(args.source, args.destination, args.format)
    executer_commande(args.command)