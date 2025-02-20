#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# URL de la page web
url = "https://plugins.qgis.org/plugins/AutoLayoutTool/#plugin-versions"

# Nom du fichier CSV
csv_file = "downloads_log.csv"

# Effectuer la requête HTTP
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    # Trouver la première occurrence de <td class="downloads">
    downloads_td = soup.find("td", class_="downloads")

    if downloads_td:
        downloads_value = downloads_td.text.strip()
    else:
        downloads_value = "0"  # Valeur par défaut en cas de problème

    # Obtenir la date et l'heure actuelles
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Écrire les données dans un fichier CSV
    with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([now, downloads_value])

    print(f"Donnée enregistrée : {now}, {downloads_value}")

    # Charger les données pour le graphique
    df = pd.read_csv(csv_file, names=["Date", "Downloads"])
    df["Date"] = pd.to_datetime(df["Date"])
    df["Downloads"] = pd.to_numeric(df["Downloads"], errors="coerce")

    # Générer le graphique
    plt.figure(figsize=(10, 5))
    plt.plot(df["Date"], df["Downloads"], marker="o", linestyle="-", color="b")
    plt.xlabel("Date")
    plt.ylabel("Nombre de téléchargements")
    plt.title("Évolution des téléchargements du plugin AutoLayoutTool")
    plt.xticks(rotation=45)
    plt.grid(True)

    # Sauvegarder en PNG
    plt.savefig("downloads_plot.png")
    plt.close()

    print("Graphique généré : downloads_plot.png")

else:
    print(f"Échec de la requête. Code : {response.status_code}")
