# Carnet de santé de la femme — version bilingue

Application Flask avec deux langues (français/arabe), écran d’accueil avec choix de l’espace femme ou professionnel de santé, carnet personnel et vue synthétique d’activité.

## Installation
1. Python 3.10+ recommandé.
2. `python -m venv .venv` puis activation.
3. `pip install -r requirements.txt`
4. `python app.py`
5. Ouvrir http://127.0.0.1:5000

La base SQLite `carnet_femme.db` est créée automatiquement à côté de `app.py`.

## Important avant utilisation réelle
Cette version est une base fonctionnelle locale/démonstration. Elle ne doit pas être utilisée pour stocker des dossiers médicaux réels en production avant d'ajouter authentification par rôles, gestion multi-patientes, chiffrement, sauvegardes, journal d'audit, protection CSRF, hébergement conforme et validation réglementaire au Maroc. La vue professionnelle calcule les volumes d'enregistrements de cette installation, pas des taux de couverture populationnelle.
