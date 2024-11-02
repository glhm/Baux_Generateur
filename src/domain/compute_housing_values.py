from src.utils.months import *

def compute_housing_values(chambre_dict, jour_arrivee, mois_arrivee):
    """
    Calcule les montants proratisés pour le premier mois de loyer et charges.
    
    :param chambre_dict: Dictionnaire contenant les informations de la chambre.
    :param jour_arrivee: Jour d'arrivée du locataire.
    :param mois_arrivee: Mois d'arrivée du locataire.
    :return: Dictionnaire avec les montants proratisés calculés.
    """
    loyer = chambre_dict['{MONTANT_LOYER}']
    charges = chambre_dict['{MONTANT_CHARGES}']
    loyer_CC = loyer + charges
    
    dernier_jour = map_jour[mois_arrivee]
    nombre_de_jours_premier_mois = dernier_jour - jour_arrivee + 1
    prorata_total_CC = nombre_de_jours_premier_mois * loyer_CC / dernier_jour
    prorata_loyer = loyer * prorata_total_CC / loyer_CC
    prorata_charges = charges * prorata_total_CC / loyer_CC
    total_premier_mois = prorata_total_CC + 2 * loyer
    montant_garanties = 2 * loyer

    return {
        "prorata_total_CC": prorata_total_CC,
        "prorata_loyer": prorata_loyer,
        "prorata_charges": prorata_charges,
        "total_premier_mois": total_premier_mois,
        "montant_garanties": montant_garanties,
        "loyer_CC": loyer_CC,
        "dernier_jour": dernier_jour,
        "nombre_de_jours_premier_mois": nombre_de_jours_premier_mois,
        "loyer": loyer,
        "charges": charges
    }
