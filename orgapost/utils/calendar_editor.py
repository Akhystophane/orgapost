import json
from datetime import datetime, timedelta
import os


def update_calendar(calendar_file, folder_path, platforms, account_name, timeslots, start_date):
    """
    Met à jour le calendrier en répartissant les posts dans les timeslots sur les plateformes,
    en itérant systématiquement après chaque changement de timeslot, et sauvegarde les résultats.

    Args:
        calendar_file (str): Chemin du fichier Calendar.json.
        folder_path (str): Le chemin du dossier contenant les sous-dossiers numérotés.
        platforms (list): Liste des plateformes (e.g., ["TikTok", "Instagram"]).
        account_name (str): Le nom du compte à mettre à jour ou ajouter.
        timeslots (list): Liste des horaires au format "HH:MM".
        start_date (str): La date de départ au format "DD:MM:YYYY".

    Returns:
        None
    """
    # Charger le calendrier existant depuis le fichier
    if os.path.exists(calendar_file):
        with open(calendar_file, "r") as file:
            calendar = json.load(file)
    else:
        calendar = {}

    # Créer le compte s'il n'existe pas
    if account_name not in calendar:
        calendar[account_name] = {"posts": []}

    # Charger tous les sous-dossiers (folder paths) et trier par numéro
    subfolders = sorted(
        [os.path.join(folder_path, subfolder) for subfolder in os.listdir(folder_path)],
        key=lambda x: int(os.path.basename(x)) if os.path.basename(x).isdigit() else float('inf')
    )

    # Convertir start_date en objet datetime
    current_date = datetime.strptime(start_date, "%d:%m:%Y")

    # Initialiser un compteur pour itérer sur les sous-dossiers
    folder_index = 0

    # Répartir les posts
    while folder_index < len(subfolders):
        for timeslot in timeslots:
            # Si tous les sous-dossiers sont utilisés, arrêter l'itération
            if folder_index >= len(subfolders):
                break

            # Récupérer le sous-dossier actuel
            subfolder = subfolders[folder_index]

            # Créer un post pour chaque plateforme
            for platform in platforms:
                post = {
                    "platform": platform,
                    "date": current_date.strftime("%d:%m:%Y"),
                    "time": timeslot,
                    "folder_path": subfolder,
                    "scheduled": False
                }
                calendar[account_name]["posts"].append(post)

            # Avancer dans la liste des sous-dossiers
            folder_index += 1

        # Passer au jour suivant
        current_date += timedelta(days=1)

    # Sauvegarder les modifications dans le fichier Calendar.json
    with open(calendar_file, "w") as file:
        json.dump(calendar, file, indent=4)
    print(f"Calendar updated and saved to {calendar_file}.")

folder_path = "/Users/emmanuellandau/Documents/data_insta/astro/9_en"

update_calendar('../database/calendar.json', folder_path, ['tiktok'], 'en_astrologenial', ['17:00', '18:00', '19:00'], "22:01:2025")