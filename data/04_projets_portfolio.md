# Portfolio de Projets Techniques

## Assistant d'Automatisation Temps Réel "LCU" (Projet Personnel)

* **Type** : Ingénierie Logicielle / Open Source
* **Contexte** : Développement d'une alternative "Privacy-First" aux solutions commerciales d'overlays de jeu, nécessitant une haute performance.
* **Architecture Technique** :
* **Langage** : **Python** (Programmation asynchrone avec `asyncio` et `aiohttp`).
* **API & Backend** : Reverse engineering et interaction directe avec l'API locale non documentée (LCU API) via requêtes HTTPS sécurisées.
* **Optimisation** : Utilisation de `ttkbootstrap` pour garantir une empreinte mémoire minimale (<50Mo RAM) et une réactivité immédiate.
* **DevOps** : Pipeline de build automatisé avec **PyInstaller** pour la distribution d'un exécutable unique (.exe).


* **Compétences Démontrées** : Architecture événementielle, Gestion de sockets temps réel, Respect de la confidentialité des données (zéro télémétrie).
* **Code Source** : [github.com/qurnt1/main_lol_2](https://github.com/qurnt1/main_lol_2.git)

## Application "Flux Manager" (Projet Groupama)

* **Type** : Outil Métier / Data Engineering
* **Problème** : Processus critique de suivi d'activité reposant sur des centaines de fichiers Excel décentralisés, engendrant des erreurs de consolidation et une maintenance lourde.
* **Solution Technique** :
* **Application Desktop** : Conception d'une GUI moderne et ergonomique avec **CustomTkinter** pour la saisie utilisateur.
* **Architecture de Données** : Centralisation des flux dans une structure standardisée (CSV/SQL), éliminant la redondance des fichiers.
* **Déploiement** : Packaging de l'environnement Python en exécutable autonome (.exe) pour un déploiement "Zero-Config" sur les postes agents.


* **Impact** : Fiabilisation à 100% de la consolidation des données RH et suppression de la charge de maintenance annuelle des fichiers Excel.

## Pipeline de Données & Sondage "Viséo 17" (Projet CCI)

* **Type** : Analyse Statistique / Data Management
* **Objectif** : Optimiser le taux de réponse et les coûts de l'enquête annuelle économique départementale.
* **Méthodologie** :
* **Échantillonnage** : Mise en place d'un sondage stratifié sur une base de 40 000 entreprises (Critères : Secteur, Taille, Localisation).
* **Data Cleaning** : Nettoyage et normalisation de bases hétérogènes pour préparer l'injection dans les outils de visualisation.
* **Contrainte Technique** : Développement de requêtes complexes sous **SQL (Access)** et **Excel** pour contourner les limitations logicielles de l'environnement client.


* **Impact** : Réduction significative des coûts d'impression (ciblage papier optimisé) et production d'indicateurs fiables pour les décideurs locaux.