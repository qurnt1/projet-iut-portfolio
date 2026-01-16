import os
import glob
from dotenv import load_dotenv
from upstash_vector import Index

load_dotenv()

# Connexion
index = Index(os.getenv("UPSTASH_VECTOR_REST_URL"), os.getenv("UPSTASH_VECTOR_REST_TOKEN"))

# Réinitialisation des index déjà existants
index.reset()
print("Anciens index supprimés.")

# création de la liste des données à indexer
vectors = []

# Parcours des fichiers et découpage
for filepath in glob.glob("data/*.md"):
    with open(filepath, "r", encoding="utf-8") as f:
        # séparation par sections via les titres de niveau 2 (##)
        # Note : le premier chunk sera l'intro (avant le premier ##)
        chunks = f.read().split("\n## ")
        
        # Ajout des chunks à la liste des vecteurs
        for i, content in enumerate(chunks):
            if content.strip():
                # On reconstruit le titre pour le contexte, sauf pour le préambule
                text = f"## {content}" if i > 0 else content
                vectors.append({
                    "id": f"{os.path.basename(filepath)}_{i}",
                    "data": text.strip(),
                    "metadata": {"source": os.path.basename(filepath)}
                })

# Envoi groupé (batch)
if vectors:
    index.upsert(vectors)
    print(f"✅ Succès : {len(vectors)} sections indexées depuis {len(glob.glob('data/*.md'))} fichiers.")