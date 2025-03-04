from src.utils.date_utils import *
#TODO pas retourner un dict...
def compute_housing_values(loyer_dict, jour_arrivee, mois_arrivee):
    """
    Calcule les montants proratisés pour le premier mois de loyer et charges.
    
    :param chambre_dict: Dictionnaire contenant les informations de la chambre.
    :param jour_arrivee: Jour d'arrivée du locataire.
    :param mois_arrivee: Mois d'arrivée du locataire.
    :return: Dictionnaire avec les montants proratisés calculés.
    """
    loyer = float(loyer_dict['{MONTANT_LOYER}'])
    charges = float(loyer_dict['{MONTANT_CHARGES}'])
    loyer_CC = loyer + charges

    dernier_jour_du_premier_mois = map_mois_to_dernier_jour[mois_arrivee]
    nombre_de_jours_premier_mois = dernier_jour_du_premier_mois - jour_arrivee + 1
    
    # Calcul du ratio de jours pour le premier et le dernier mois
    ratio_premier_mois = nombre_de_jours_premier_mois / dernier_jour_du_premier_mois
    
    # Calcul des montants proratisés
    prorata_total_CC = round(ratio_premier_mois * loyer_CC, 2)
    prorata_loyer = round(ratio_premier_mois * loyer, 2)
    prorata_charges = round(ratio_premier_mois * charges, 2)
    
    total_premier_mois = round(prorata_total_CC + 2 * loyer, 2)
    montant_garanties = round(2 * loyer, 2)
    
    return {
        "prorata_total_CC": prorata_total_CC,
        "prorata_loyer": prorata_loyer,
        "prorata_charges": prorata_charges,
        "nombre_de_jours_premier_mois": nombre_de_jours_premier_mois,

        "total_premier_mois": total_premier_mois,
        "montant_garanties": montant_garanties,

        "loyer_CC": loyer_CC,
        "loyer": loyer,
        "charges":charges,
    }

def compute_departure_values(loyer_dict,jour_depart,mois_depart):
    loyer = float(loyer_dict['{MONTANT_LOYER}'])
    charges = float(loyer_dict['{MONTANT_CHARGES}'])
    loyer_CC = loyer + charges

    # Calcul du ratio de jours pour le premier et le dernier mois
    ratio_dernier_mois = jour_depart / get_dernier_jour_du_mois_par_numero(mois_depart) #TODO try le error
    
    prorata_total_CC_depart = round(ratio_dernier_mois * loyer_CC, 2)
    prorata_loyer_depart = round(ratio_dernier_mois * loyer, 2)
    prorata_charges_depart = round(ratio_dernier_mois * charges, 2)
    
    
    return {
        "prorata_total_CC_depart": prorata_total_CC_depart,
        "prorata_loyer_depart": prorata_loyer_depart,
        "prorata_charges_depart": prorata_charges_depart

    }



def calculate_prorata(locataire, chambre_dict):
    mois_arrivee = locataire['properties']['{MOIS_ARRIVEE}']['rich_text'][0]['text']['content']
    jour_arrivee = locataire['properties']['{JOUR_ARRIVEE}']['number']
    return compute_housing_values(chambre_dict, jour_arrivee, mois_arrivee)
