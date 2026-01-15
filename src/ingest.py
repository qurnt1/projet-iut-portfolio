"""
Script d'indexation des données du portfolio dans Upstash Vector.
Ce script doit être exécuté une seule fois pour charger les données initiales.

Utilisation:
    python ingest.py
"""

import os
import re
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from upstash_vector import Index

# Charger les variables d'environnement
load_dotenv()


def load_markdown_file(file_path: Path) -> str:
    """
    Charge le contenu d'un fichier Markdown.
    
    Args:
        file_path: Chemin vers le fichier Markdown
        
    Returns:
        Contenu du fichier sous forme de chaîne
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Erreur lors de la lecture de {file_path}: {e}")
        return ""


def chunk_markdown_by_headings(content: str, source_file: str) -> List[Dict[str, str]]:
    """
    Découpe un document Markdown en chunks basés sur les titres (# et ##).
    Chaque section devient un chunk cohérent avec ses métadonnées.
    
    Args:
        content: Contenu du fichier Markdown
        source_file: Nom du fichier source
        
    Returns:
        Liste de dictionnaires contenant le texte et les métadonnées
    """
    chunks = []
    
    # Séparer par les titres de niveau 1 et 2
    # On garde le titre avec le contenu qui suit
    sections = re.split(r'(^#{1,2}\s+.+$)', content, flags=re.MULTILINE)
    
    current_title = ""
    current_content = ""
    
    for i, section in enumerate(sections):
        section = section.strip()
        if not section:
            continue
            
        # Vérifier si c'est un titre
        if re.match(r'^#{1,2}\s+', section):
            # Sauvegarder le chunk précédent s'il existe
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
            current_content += section + "\n"
    
    # Ajouter le dernier chunk
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
    Indexe les chunks dans Upstash Vector.
    
    Args:
        chunks: Liste des chunks à indexer
        index: Instance de l'index Upstash Vector
        
    Returns:
        Nombre de chunks indexés avec succès
    """
    indexed_count = 0
    
    for i, chunk in enumerate(chunks):
        try:
            # Upstash Vector en mode Hybrid génère automatiquement les embeddings
            # On envoie simplement le texte brut avec les métadonnées
            index.upsert(
                vectors=[{
                    "id": f"chunk_{i}_{chunk['metadata']['source']}",
                    "data": chunk["text"],
                    "metadata": chunk["metadata"]
                }]
            )
            indexed_count += 1
            print(f"Chunk {i+1}/{len(chunks)} indexé: {chunk['metadata']['title'][:50]}...")
        except Exception as e:
            print(f"Erreur lors de l'indexation du chunk {i}: {e}")
    
    return indexed_count


def main():
    """
    Fonction principale d'indexation.
    """
    print("🚀 Démarrage de l'indexation du portfolio...")
    
    # Vérifier les variables d'environnement
    upstash_url = os.getenv("UPSTASH_VECTOR_REST_URL")
    upstash_token = os.getenv("UPSTASH_VECTOR_REST_TOKEN")
    
    if not upstash_url or not upstash_token:
        print("❌ Erreur: Variables d'environnement UPSTASH_VECTOR_REST_URL et/ou UPSTASH_VECTOR_REST_TOKEN manquantes.")
        print("💡 Assurez-vous d'avoir créé un fichier .env à partir de .env.example")
        return
    
    # Connexion à Upstash Vector
    try:
        index = Index(url=upstash_url, token=upstash_token)
        print("✅ Connexion à Upstash Vector réussie")
    except Exception as e:
        print(f"❌ Erreur de connexion à Upstash Vector: {e}")
        return
    
    # Récupérer tous les fichiers Markdown du dossier data/
    data_dir = Path("data")
    if not data_dir.exists():
        print(f"❌ Erreur: Le dossier {data_dir} n'existe pas")
        return
    
    markdown_files = list(data_dir.glob("*.md"))
    if not markdown_files:
        print(f"❌ Aucun fichier .md trouvé dans {data_dir}")
        return
    
    print(f"📁 {len(markdown_files)} fichiers Markdown trouvés")
    
    # Traiter chaque fichier
    all_chunks = []
    for md_file in sorted(markdown_files):
        print(f"\n📄 Traitement de {md_file.name}...")
        content = load_markdown_file(md_file)
        
        if content:
            chunks = chunk_markdown_by_headings(content, md_file.name)
            all_chunks.extend(chunks)
            print(f"   ✅ {len(chunks)} chunks créés")
    
    print(f"\n📊 Total: {len(all_chunks)} chunks à indexer")
    
    # Indexation dans Upstash
    print("\n🔄 Indexation en cours...")
    indexed = index_data_to_upstash(all_chunks, index)
    
    print(f"\n🎉 Indexation terminée: {indexed}/{len(all_chunks)} chunks indexés avec succès")
    
    # Vérification
    try:
        info = index.info()
        print(f"📈 Statistiques de l'index:")
        print(f"   - Dimension: {info.dimension}")
        print(f"   - Total vecteurs: {info.vector_count}")
    except Exception as e:
        print(f"⚠️ Impossible de récupérer les statistiques: {e}")


if __name__ == "__main__":
    main()
