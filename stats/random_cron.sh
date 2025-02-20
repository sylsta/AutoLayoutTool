#!/bin/bash

# Générer un nombre entre 11 et 13
HOUR1=$((RANDOM % 3 + 11))

# Générer un nombre entre 16 et 19
HOUR2=$((RANDOM % 3 + 15))

# Générer des minutes aléatoires
MINUTE1=$((RANDOM % 60))  # 0-59
MINUTE2=$((RANDOM % 60))  # 0-59

# Définir le chemin du script Python
SCRIPT_PATH="/usr/bin/python3 /home/sylter/Cloud/github.com/AutoLayoutTool/stats/check_dl_stat.py"

# Définir la ligne pour s'auto-appeler chaque jour à 10h59
CRON_SELF="59 10 * * * /home/sylter/Cloud/github.com/AutoLayoutTool/stats/random_cron.sh"

# Définir les nouvelles lignes cron
CRON_JOB1="$MINUTE1 $HOUR1 * * * $SCRIPT_PATH"
CRON_JOB2="$MINUTE2 $HOUR2 * * * $SCRIPT_PATH"

# Supprimer toutes les anciennes occurrences de `check_dl_stat.py` et `random_cron.sh` du crontab
(crontab -l | grep -v -F "$SCRIPT_PATH" | grep -v -F "$CRON_SELF") | crontab -

# Ajouter les nouvelles lignes dans le crontab
(crontab -l; echo "$CRON_SELF"; echo "$CRON_JOB1"; echo "$CRON_JOB2") | crontab -

echo "Tâches planifiées à $HOUR1:$MINUTE1 et $HOUR2:$MINUTE2"