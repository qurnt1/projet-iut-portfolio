"""
Script d'indexation des données du portfolio dans Upstash Vector.

Ce module gère le pipeline d'ingestion des fichiers Markdown du portfolio :
    1. Chargement des fichiers .md depuis le dossier data/
    2. Découpage intelligent par sections (titres # et ##)
    3. Indexation dans Upstash Vector pour la recherche hybride

Usage:
    python ingest.py

Note:
    Ce script doit être exécuté une seule fois pour charger les données initiales,
    ou à chaque mise à jour du contenu du portfolio.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional

from dotenv import load_dotenv
from upstash_vector import Index

# Chargement des variables d'environnement depuis .env
load_dotenv()


def load_markdown_file(file_path: Path) -> str:
    """
    Charge le contenu d'un fichier Markdown.

    Args:
        file_path: Chemin absolu ou relatif vers le fichier Markdown à lire.

    Returns:
        Contenu brut du fichier sous forme de chaîne de caractères.
        Retourne une chaîne vide en cas d'erreur de lecture.

    Raises:
        Aucune exception levée directement ; les erreurs sont capturées
        et loguées dans la console.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Erreur lors de la lecture de {file_path}: {e}")
        return ""


def chunk_markdown_by_headings(content: str, source_file: str) -> List[Dict[str, str]]:
    """
    Découpe un document Markdown en chunks basés sur les titres.

    Chaque section délimitée par un titre de niveau 1 (#) ou 2 (##) devient
    un chunk indépendant avec ses métadonnées associées.

    Args:
        content: Contenu brut du fichier Markdown à découper.
        source_file: Nom du fichier source (utilisé dans les métadonnées).

    Returns:
        Liste de dictionnaires, chacun contenant :
            - "text": Le contenu textuel du chunk (titre + corps).
            - "metadata": Dict avec "source" (nom fichier) et "title" (titre section).

    Example:
        >>> chunks = chunk_markdown_by_headings("# Titre\\nContenu", "cv.md")
        >>> chunks[0]["metadata"]["title"]
        'Titre'
    """
    chunks: List[Dict[str, str]] = []

    # Regex pour séparer le contenu par titres H1/H2 tout en conservant les délimiteurs
    sections = re.split(r'(^#{1,2}\s+.+$)', content, flags=re.MULTILINE)

    current_title: str = ""
    current_content: str = ""

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Détection d'un titre Markdown (commence par # ou ##)
        if re.match(r'^#{1,2}\s+', section):
            # Sauvegarder le chunk précédent avant de passer au suivant
            if current_content:
                chunks.append({
                    "text": f"{current_title}\n\n{current_content}".strip(),
                    "metadata": {
                        "source": source_file,
                        "title": current_title.strip('#').strip()
                    }
                })

            current_title = section
            current_content = ""
        else:
            # Accumulation du contenu sous le titre courant
            current_content += section + "\n"

    # Ajout du dernier chunk (après la dernière section)
    if current_content:
        chunks.append({
            "text": f"{current_title}\n\n{current_content}".strip(),
            "metadata": {
                "source": source_file,
                "title": current_title.strip('#').strip() if current_title else "Introduction"
            }
        })

    return chunks


def index_data_to_upstash(chunks: List[Dict[str, str]], index: Index) -> int:
    """
    Indexe les chunks dans Upstash Vector via upsert.

    Utilise le mode Hybrid d'Upstash qui génère automatiquement les embeddings
    (dense via BAAI/bge-m3 + sparse via BM25).

    Args:
        chunks: Liste des chunks à indexer (chacun avec "text" et "metadata").
        index: Instance de l'index Upstash Vector initialisée.

    Returns:
        Nombre de chunks indexés avec succès.

    Raises:
        Aucune exception levée directement ; les erreurs sont capturées
        et loguées dans la console pour chaque chunk.
    """
    indexed_count: int = 0

    for i, chunk in enumerate(chunks):
        try:
            # Upsert : insertion ou mise à jour si l'ID existe déjà
            index.upsert(
                vectors=[{
                    "id": f"chunk_{i}_{chunk['metadata']['source']}",
                    "data": chunk["text"],  # Texte brut pour embedding automatique
                    "metadata": chunk["metadata"]
                }]
            )
            indexed_count += 1
            print(f"Chunk {i+1}/{len(chunks)} indexé: {chunk['metadata']['title'][:50]}...")
        except Exception as e:
            print(f"Erreur lors de l'indexation du chunk {i}: {e}")

    return indexed_count


def main() -> None:
    """
    Fonction principale orchestrant le pipeline d'indexation.

    Étapes exécutées :
        1. Validation des variables d'environnement Upstash
        2. Connexion à l'index Upstash Vector
        3. Lecture de tous les fichiers .md du dossier data/
        4. Découpage en chunks par sections Markdown
        5. Indexation dans Upstash Vector
        6. Affichage des statistiques finales

    Returns:
        None

    Raises:
        Aucune exception levée ; le script s'arrête proprement en cas d'erreur
        de configuration ou de connexion.
    """
    print("🚀 Démarrage de l'indexation du portfolio...")

    # --- Étape 1 : Validation des credentials Upstash ---
    upstash_url: Optional[str] = os.getenv("UPSTASH_VECTOR_REST_URL")
    upstash_token: Optional[str] = os.getenv("UPSTASH_VECTOR_REST_TOKEN")

    if not upstash_url or not upstash_token:
        print("❌ Erreur: Variables d'environnement UPSTASH_VECTOR_REST_URL et/ou UPSTASH_VECTOR_REST_TOKEN manquantes.")
        print("💡 Assurez-vous d'avoir créé un fichier .env à partir de .env.example")
        return

    # --- Étape 2 : Connexion à Upstash Vector ---
    try:
        index = Index(url=upstash_url, token=upstash_token)
        print("✅ Connexion à Upstash Vector réussie")
    except Exception as e:
        print(f"❌ Erreur de connexion à Upstash Vector: {e}")
        return

    # --- Étape 3 : Découverte des fichiers Markdown ---
    data_dir = Path("data")
    if not data_dir.exists():
        print(f"❌ Erreur: Le dossier {data_dir} n'existe pas")
        return

    markdown_files: List[Path] = list(data_dir.glob("*.md"))
    if not markdown_files:
        print(f"❌ Aucun fichier .md trouvé dans {data_dir}")
        return

    print(f"📁 {len(markdown_files)} fichiers Markdown trouvés")

    # --- Étape 4 : Traitement et chunking ---
    all_chunks: List[Dict[str, str]] = []
    for md_file in sorted(markdown_files):
        print(f"\n📄 Traitement de {md_file.name}...")
        content = load_markdown_file(md_file)

        if content:
            chunks = chunk_markdown_by_headings(content, md_file.name)
            all_chunks.extend(chunks)
            print(f"   ✅ {len(chunks)} chunks créés")

    print(f"\n📊 Total: {len(all_chunks)} chunks à indexer")

    # --- Étape 5 : Indexation dans Upstash ---
    print("\n🔄 Indexation en cours...")
    indexed = index_data_to_upstash(all_chunks, index)

    print(f"\n🎉 Indexation terminée: {indexed}/{len(all_chunks)} chunks indexés avec succès")

    # --- Étape 6 : Vérification et statistiques ---
    try:
        info = index.info()
        print(f"📈 Statistiques de l'index:")
        print(f"   - Dimension: {info.dimension}")
        print(f"   - Total vecteurs: {info.vector_count}")
    except Exception as e:
        print(f"⚠️ Impossible de récupérer les statistiques: {e}")


if __name__ == "__main__":
    main()
