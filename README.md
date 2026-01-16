#  Portfolio Interactif avec Agent IA Groq

Agent conversationnel intelligent construit avec **Groq** pour explorer interactivement un portfolio. Utilise la génération augmentée par récupération (RAG) avec une base de données vectorielle et est déployé sur **Streamlit**.

**[ Essayer l'application](https://portfolio-llm-quentin.streamlit.app/) | [ Code source](https://github.com/qurnt1/projet-iut-portfolio.git)**

## À propos

Ce projet crée une expérience conversationnelle unique où les visiteurs peuvent poser des questions sur les expériences, compétences et projets de Quentin. L'agent IA répond intelligemment en puisant dans vos données de profil.

## Fonctionnalités

- ** Chat intelligent** - Interaction naturelle avec un agent IA
- ** RAG (Retrieval-Augmented Generation)** - Réponses contextuelles basées sur vos données
- ** Groq** - LLM ultra-rapide et performant
- ** Interface Streamlit** - Interface utilisateur intuitive et moderne
- ** Déployé en ligne** - Accessible directement via le web

## Architecture

`
data/                          # Profil en fichiers Markdown
 01_profil_bio.md
 02_competences_techniques.md
 03_experiences_pro_*.md
 ...

src/
 agent.py                   # Agent IA avec Groq
 app.py                     # Interface Streamlit
 ingest_data.py            # Ingestion & indexation des données
`

## Installation locale

1. **Clone le repository**
```bash
git clone https://github.com/qurnt1/projet-iut-portfolio.git
cd projet-iut-portfolio
```

2. **Crée un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installe les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configure les variables d'environnement**
Crée un fichier .env avec tes clés API Groq et autres configurations nécessaires.

5. **Lance l'app**
```bash
streamlit run src/app.py
```

## Utilisation

Ouvre l'application et pose des questions sur le profil :
- "Quelles sont tes compétences techniques ?"
- "Parle-moi de ton expérience..."
- "Quels projets as-tu réalisés ?"

L'agent analyse tes données et répond de manière pertinente et conversationnelle.

## Technologies utilisées

- **Groq** - LLM performant
- **Streamlit** - Framework web
- **Upstash Vector** - Base de données vectorielle
- **Python 3.12+**

##  Liens

- [Application en ligne](https://portfolio-llm-quentin.streamlit.app/)
- [Repository GitHub](https://github.com/qurnt1/projet-iut-portfolio.git)
