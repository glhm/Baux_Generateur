# Baux_Generateur
Leases_Generator

Générateur de Baux
Un outil automatisé pour la génération de baux résidentiels basé sur les données de locataires, garants et propriétés. 
Intégré avec Notion pour la gestion des données et Google Docs pour la génération de documents.

-------------------------------------------------------------------------------------------------------------------

Fonctionnalités

Récupération automatique des données des locataires, garants, biens, chambres et propriétés depuis Notion.
Création automatisée de documents Google Docs basés sur un modèle prédéfini.
Possibilité de personnaliser les modèles de baux.
Exportation des baux générés au format PDF.

-------------------------------------------------------------------------------------------------------------------
 Prérequis
> Configurer dans le code l'id de votre Template Google de baux et d'acte de caution
> Compte Notion avec les bases de données appropriées configurées.
> Accès API Notion activé.
> Compte Google avec Google Docs et Drive.
> Accès API Google activé.
> python -m venv venv (configurer env virtuel)
> Créer un répo mysecrets/ et un fichier  notion_secrets.py 
 avec 
 NOTION_API_SECRET = "key_to_your_notion_integration"
DATABASE_IDS = {
     "bien": "Id of ur Bien database",
    "locataire": "Id of ur Bien database",
     "chambres": "Id of ur Chambres database",
     "garants": "a3f2eaf45ee34d2bbf58922af689e941"
}
CLIENT_GOOGLE_SECRET_JSON_PATH = "path_to_google_api_secret_client.json"

> Dans le repo "pip install -r requirements.txt
> Assurez-vous d'avoir configuré vos bases de données Notion avec des colonnes nommées {COLONNE} et les données nécessaires. Dans le fichier le texte à remplacer doit être de la forme {{COLONNE}}


--------------------------------------------------------------------------------------------------------------------
Execution 
> venv\Scripts\activate
> python main.py
Les baux générés seront exportés en format PDF et dans votre drive format google doc


