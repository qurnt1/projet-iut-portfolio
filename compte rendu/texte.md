projet portfolio avec un Retrieval-Augmented Generation
il ets possible de tester l'application sur le lien suivant :
https://portfolio-llm-quentin.streamlit.app/

intro :
j'ai du dans le cadre d'un cours de BUT 3 science des données, supervisé par théo koessler créer un agent ia de portfolio, qui réponds a toute les questions sur mon parcours et ma personne, avec l'aide de l'outil upstash () et un agent ia propulsé par une clef api groq et le modele openai/gpt-oss-120b
1. qu'est ce qu'un RAG, et comment l'utiliser
2. les codes pythons du projet :
    2.1 l'ingestion des données
    2.2 l'agent ia
    2.3 l'interface

1. qu'est ce qu'un RAG, et comment l'utiliser

Comprendre le RAG (Retrieval-Augmented Generation)

Le RAG, ou Génération Augmentée par la Récupération, est une architecture informatique conçue pour pallier les limites des modèles de langage classiques. Plutôt que de se reposer uniquement sur les connaissances acquises lors de son entraînement, qui peuvent être obsolètes ou incomplètes, cette technologie permet à l'IA d'accéder à une base de données externe en temps réel. Son rôle principal est de servir de pont entre l'intelligence générative et une source d'informations fiable, garantissant ainsi que les réponses produites soient basées sur des faits concrets et vérifiables plutôt que sur des spéculations.

Le fonctionnement technique repose sur un cycle structuré commençant par l'indexation, où les documents du projet sont convertis en vecteurs numériques pour être stockés. Lorsqu'un utilisateur pose une question, le système effectue une phase de récupération en identifiant les segments d'information les plus pertinents dans la base de données. Enfin, la phase de génération intervient : le modèle de langage reçoit la question initiale accompagnée de ces extraits de texte précis pour rédiger une réponse synthétique. Cette méthode élimine virtuellement les risques d'hallucination, puisque l'IA est contrainte de justifier ses propos par les documents qui lui sont fournis.

Dans le cadre de ce projet, l'infrastructure s'appuie sur la solution Upstash Vector déployée sur les serveurs AWS en Irlande. Pour maximiser la précision, la configuration utilise une recherche hybride combinant deux approches complémentaires. D'un côté, le modèle bge-m3 analyse la sémantique profonde pour comprendre l'intention derrière les mots, tandis que l'algorithme BM25 assure une correspondance stricte par mots-clés. Cette synergie garantit que le système retrouve les informations avec une exactitude rigoureuse, que la recherche porte sur un concept général ou sur un terme technique spécifique propre au portfolio.


2. les codes pythons du projet :
2.1 l'ingestion des données

Le script src/ingest_data.py remplit la fonction critique d'alimentation de la base de connaissances en transformant des documents bruts en données exploitables par l'intelligence artificielle. Son exécution commence par une phase de sécurisation et de nettoyage : il charge les identifiants de connexion via des variables d'environnement pour accéder à l'instance Upstash Vector, puis procède à une réinitialisation complète de l'index. Cette étape de suppression systématique des anciennes données est une mesure de rigueur qui garantit l'intégrité de la base, évitant ainsi les doublons ou la persistance d'informations obsolètes lors des mises à jour du portfolio.

Le cœur du script repose sur une logique de segmentation intelligente, appelée "chunking", appliquée aux fichiers Markdown du dossier source. Plutôt que d'importer les documents en un seul bloc massif, ce qui nuirait à la précision des recherches, le code utilise les titres de niveau deux (##) comme séparateurs naturels. Cette stratégie permet de découper le parcours de Quentin Chabot en unités logiques cohérentes, telles que des projets spécifiques ou des blocs de compétences distincts. Chaque segment ainsi créé est enrichi de métadonnées indiquant sa source d'origine, garantissant une traçabilité totale lors de la phase de récupération par l'agent.

Enfin, le script optimise les performances réseau et la rapidité de traitement grâce à une opération d'envoi groupé, ou "batch upsert". Au lieu d'envoyer chaque fragment d'information individuellement, le programme compile l'ensemble des vecteurs dans une liste unique pour les injecter massivement dans la base de données en une seule requête. Cette approche industrielle réduit drastiquement le temps d'indexation et assure que le portfolio est immédiatement prêt à être interrogé par l'agent conversationnel. En résumé, ce script automatise la transformation de fichiers textes statiques en une mémoire vive et structurée, indispensable au bon fonctionnement du système RAG.

2. les codes pythons du projet :
2.2 l'agent ia

Le fichier src/agent.py constitue le moteur décisionnel du projet, transformant un modèle de langage classique en un agent autonome capable d'interagir intelligemment avec des données externes. Cette architecture repose sur la définition d'un outil spécialisé, la fonction search_portfolio, qui sert de pont technique entre l'intelligence artificielle et la base de données vectorielle Upstash. Lorsqu'une question est posée, cet outil active une recherche ciblée en récupérant les six segments d'information les plus pertinents mathématiquement. Chaque fragment est automatiquement associé à ses métadonnées, comme le titre ou la source, afin de fournir à l'IA un contexte riche et vérifiable sur le parcours de Quentin Chabot.

La configuration de l'objet Agent définit ensuite la "personnalité" et les règles de conduite du système. Contrairement à un chatbot générique, cet agent est programmé avec des instructions strictes lui imposant un ton professionnel, direct et analytique, tout en lui interdisant les formules de politesse superflues ou les aveux d'impuissance face à une information manquante. Le code intègre également une logique de synthèse qui oblige l'IA à combiner différents blocs de données (formation, expériences, compétences) pour produire une réponse cohérente et structurée. L'ensemble est propulsé par l'infrastructure Groq, garantissant une vitesse d'exécution optimale du modèle, ce qui permet à l'agent de traiter la donnée et de formuler une analyse experte en une fraction de seconde. En résumé, ce script orchestre la récupération de l'information brute et sa transformation en une réponse argumentée, alignée sur les standards de rigueur d'un consultant senior.

2. les codes pythons du projet :
2.3 l'interface

disclaimer : 
pour cette partie du code, meme si dans le sujet il était explicité de ne pas utiliser d'ia et de ne pas utiliser d'html, j'avoue j'en ai quand meme utilisé, j'ai essayé au départ sans ia ni html et ai reussi en suivant les liens que vous nous aviez donné dans le readme, et en suivant le cours que vous aviez présenté en direct de création de l'interface, mais comme je veux mettre se projet en avant sur mon vrai portfolio, et donner l'acces a d'autres personnes et potentiellement de futurs recruteurs, j'ai refais ma propre interface avec ia, apres avoir terminé sans et compris comment fonctionnait le principe, de faire en sorte que l'interface elle soit un minumum démarquée des autres et assez agréable a visualiser, sinon personne va l'utiliser et le projet aurais moins de plus value selon moi ...

le fichier src/app.py (a lancer avec  : "streamlit run app.py") l'interface se veut assez simple avec des couleurs claires et assez facile a prendre en main, il y a une zone de texte dans laquelle l'utilisateur peut ecrire au chatbot en bas, ou alors 3 boutons pour lancer une conversation si il n'a pas d'inspiration au moment ou il arrive sur la page : le parcours académique, les experiences pro, et mes compétences techniques,

j'ai fait en sorte que si le mot cv ou curriculum vitae est mentionné dans le prompt envoyé a l'agent, cela renvoie mon cv sous forme de pdf en bouton cliquable, et aussi au bout de 4 messages, l'application met en avant mes canaux pro afin d'envoyer les potentielles personnes qui sont sur mon portfolio sur mes vrais points de contact pour continuer la discussion