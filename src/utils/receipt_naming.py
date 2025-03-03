
import re

# 📌 Fonction pour générer le nom du document de quittance
def generate_quittance_doc_name(annee_courante, mois_index, formatted_name,montant1,montant2):
    mois_numero_str = f"{mois_index:02}"
    return f"Quittance--{formatted_name}{mois_numero_str}{annee_courante}--{formatted_name}--{montant1}--{montant2}"

# 📌 Fonction pour créer le motif regex de recherche des quittances
def get_quittance_pattern(current_month_num, current_year, formatted_name):
    # 📌 Motif regex pour xx entre 00 et 30
    return re.compile(rf"^Quittance--(0[0-9]|[12][0-9]|30){current_month_num}{current_year}--{formatted_name}--.*$")

