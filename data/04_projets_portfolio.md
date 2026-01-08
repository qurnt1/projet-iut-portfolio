# Portfolio de Projets Techniques

## LOL MAIN - Assistant d'Automatisation (Projet Personnel)
* **Type** : Développement Logiciel / Ingénierie
* **Objectif** : Création d'une alternative légère et respectueuse de la vie privée aux overlays gaming (type Overwolf).
* **Architecture Technique** :
    * **Langage** : Python (Architecture événementielle et asynchrone avec `asyncio`).
    * **Connexion API** : Interaction directe avec la **LCU API** (League Client Update) locale, sans scraping ni télémétrie externe.
    * **Interface (GUI)** : Utilisation de `ttkbootstrap` pour une empreinte mémoire minimale.
    * **Distribution** : Compilation en `.exe` via **PyInstaller** et orchestration via script Batch.
* **Fonctionnalités** :
    * Automatisation des phases de lobby (Acceptation, Auto-Pick, Auto-Ban).
    * Intégration de raccourcis globaux pour l'affichage de statistiques.
* **Compétences Démontrées** : Gestion de flux temps réel, optimisation CPU/RAM, déploiement d'exécutables autonomes.
* **Liens** : https://github.com/qurnt1/main_lol_2.git

## Application de Pilotage de Flux (Projet Groupama)
* **Type** : Outil Métier / Automatisation
* **Problème** : Consolidation manuelle inefficace de multiples fichiers Excel pour le suivi d'activité des collaborateurs.
* **Solution Technique** :
    * Développement d'une **application Desktop autonome** en Python.
    * **GUI** : Interface moderne développée avec **CustomTkinter**.
    * **Backend** : Centralisation des données dans des fichiers CSV structurés par équipe.
    * **Déploiement** : Transformation en exécutable `.exe` pour une utilisation "clé en main" sans installation de Python sur les postes clients.
* **Impact** : Suppression de la création annuelle de fichiers manuels, fiabilisation des données RH.

## Pipeline de Données "Viséo 17" (Projet CCI)
* **Type** : Data Engineering / Analyse
* **Solution Technique** :
    * Nettoyage et normalisation de bases de données hétérogènes (Data Cleaning).
    * Utilisation de **SQL** et **Access** pour structurer les données économiques départementales.
    * Préparation des datasets pour l'intégration dans l'outil de visualisation final.
* **Impact** : Fiabilisation des indicateurs économiques utilisés par les décideurs locaux.