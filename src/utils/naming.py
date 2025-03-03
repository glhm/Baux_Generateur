
import re

# 📌 Fonction pour générer le nom du document de quittance
def generate_quittance_doc_name(jour, mois_index, annee_courante, formatted_name, montant1, montant2):
    # Convertir les montants en chaîne et remplacer les points par 'v'
    montant1_str = f"{montant1:.2f}".replace('.', 'v')
    montant2_str = f"{montant2:.2f}".replace('.', 'v')
    
    # Générer le nom du fichier
    mois_numero_str = f"{mois_index:02}"
    return f"Quittance--{formatted_name}--{annee_courante}{mois_numero_str}{jour}--{montant1_str}--{montant2_str}"

# 📌 Fonction pour créer le motif regex de recherche des quittances
def get_quittance_pattern(current_month_num, current_year, formatted_name):
    # 📌 Motif regex pour xx entre 00 et 30
    return re.compile(rf"^Quittance--{formatted_name}--{current_year}{current_month_num}(0[0-9]|[12][0-9]|30)--.*$")


def build_formatted_name(locataire):
    formatted_name = locataire['properties']['{NOM_LOCATAIRE}']['title'][0]['text']['content'].replace(" ", "_").replace("'", "_").replace(",", "")
    return formatted_name

