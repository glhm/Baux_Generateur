# replace_strings_in_doc.py

from notion_database import *
from mystrings import *

def prepare_replace_requests(locataire_dict_str, guarant_dict_str, bien_dict_str, chambre_dict_str, prorata_data, type_caution, mention_speciale_loyer, date_contrat, type_bail):
    """
    Prépare les demandes de remplacement pour le modèle de document avec les informations fournies.

    :param locataire_dict_str: Dictionnaire avec les informations du locataire sous forme de chaîne.
    :param guarant_dict_str: Dictionnaire avec les informations du garant sous forme de chaîne.
    :param bien_dict_str: Dictionnaire avec les informations du bien sous forme de chaîne.
    :param chambre_dict_str: Dictionnaire avec les informations de la chambre sous forme de chaîne.
    :param prorata_data: Dictionnaire avec les données proratisées calculées.
    :param type_caution: Type de caution.
    :param mention_speciale_loyer: Mention spéciale du loyer.
    :param date_contrat: Date du contrat.
    :param type_bail: Type de bail.
    :return: Liste des demandes de remplacement.
    """
    all_replace_requests = []

    # Gestion des types de caution
    if type_caution == "Visale":
        all_replace_requests.extend(add_one_request("{{CAUTIONNEMENT}}", cautionnement_visale))
        all_replace_requests.extend(add_one_request("{{LA_CAUTION}}", ""))
        all_replace_requests.extend(add_one_request("{{SIGN_GARANT}}", ""))
        all_replace_requests.extend(add_one_request("{{DOC_VISA}}", doc_visale))
    else:
        all_replace_requests.extend(add_one_request("{{CAUTIONNEMENT}}", cautionnement_physique))
        all_replace_requests.extend(add_one_request("{{LA_CAUTION}}", la_caution_physique))
        all_replace_requests.extend(add_one_request("{{SIGN_GARANT}}", signature_des_garants))
        all_replace_requests.extend(add_one_request("{{DOC_VISA}}", ""))

    # Ajout des informations provenant des dictionnaires
    all_replace_requests.extend(build_replace_requests(locataire_dict_str))
    all_replace_requests.extend(build_replace_requests(guarant_dict_str))
    all_replace_requests.extend(build_replace_requests(bien_dict_str))
    all_replace_requests.extend(build_replace_requests(chambre_dict_str))

    # Ajout des informations calculées
    all_replace_requests.extend(add_one_request("{{TOTAL_1ER_MOIS}}", "{:.2f}".format(prorata_data["total_premier_mois"])))
    all_replace_requests.extend(add_one_request("{{PRORATA_TOTAL_CC}}", "{:.2f}".format(prorata_data["prorata_total_CC"])))
    all_replace_requests.extend(add_one_request("{{PRORATA_LOYER}}", "{:.2f}".format(prorata_data["prorata_loyer"])))
    all_replace_requests.extend(add_one_request("{{PRORATA_CHARGES}}", "{:.2f}".format(prorata_data["prorata_charges"])))
    all_replace_requests.extend(add_one_request("{{MONTANT_LOYER}}", str(prorata_data["loyer"])))
    all_replace_requests.extend(add_one_request("{{MONTANT_CHARGES}}", str(prorata_data["charges"])))
    all_replace_requests.extend(add_one_request("{{MONTANT_GARANTIES}}", str(prorata_data["montant_garanties"])))
    all_replace_requests.extend(add_one_request("{{MONTANT_TOTAL}}", str(prorata_data["loyer_CC"])))
    all_replace_requests.extend(add_one_request("{{DERNIER_JOUR}}", str(prorata_data["dernier_jour"])))
    all_replace_requests.extend(add_one_request("{{NOMBRE_JOURS_PREMIER_MOIS}}", str(prorata_data["nombre_de_jours_premier_mois"])))
    
    if mention_speciale_loyer:
        all_replace_requests.extend(add_one_request("{{MENTION_SPECIALE_LOYER}}", mention_speciale_loyer))
    else:
        all_replace_requests.extend(add_one_request("{{MENTION_SPECIALE_LOYER}}", ""))

    all_replace_requests.extend(add_one_request("{{DATE_CONTRAT}}", date_contrat))

    # Gestion du type de bail
    if type_bail == 'Etudiant':
        all_replace_requests.extend(add_one_request("{{PARAGRAPHE_DUREE_CONTRAT}}", bail_etudiant_duree))
        all_replace_requests.extend(add_one_request("{{TYPE_BAIL_MEUBLE}}", bail_etudiant_titre))
        all_replace_requests.extend(add_one_request("{{DUREE_CONTRAT}}", duree_contrat_etudiant))
        all_replace_requests.extend(add_one_request("{{MENTION_RECONDUCTION_MEUBLE}}", ""))

    else:
        all_replace_requests.extend(add_one_request("{{PARAGRAPHE_DUREE_CONTRAT}}", bail_meuble_duree))
        all_replace_requests.extend(add_one_request("{{MENTION_RECONDUCTION_MEUBLE}}", reconduction_meuble))
        all_replace_requests.extend(add_one_request("{{DUREE_CONTRAT}}", duree_contrat_meuble))
        all_replace_requests.extend(add_one_request("{{TYPE_BAIL_MEUBLE}}", str("")))

    return all_replace_requests


def prepare_quittance_requests(prorata_data, mois_courant, somme_due, jour_debut_quittance, titre_detail_reglement, paragraphe_detail_reglement):
    """
    Prépare les demandes de remplacement pour les quittances.

    :param prorata_data: Dictionnaire avec les données proratisées calculées.
    :param mois_courant: Mois courant pour la quittance.
    :param somme_due: Montant total dû pour la quittance.
    :param jour_debut_quittance: Jour de début de la quittance.
    :param titre_detail_reglement: Titre du détail du règlement.
    :param paragraphe_detail_reglement: Paragraphe de détail du règlement.
    :return: Liste des demandes de remplacement.
    """
    quittance_requests = []

    # Ajout des informations spécifiques à la quittance
    quittance_requests.extend(add_one_request("{{SOMME_DUE}}", "{:.2f}".format(somme_due)))
    quittance_requests.extend(add_one_request("{{JOUR_DEBUT_QUITTANCE}}", str(jour_debut_quittance)))
    quittance_requests.extend(add_one_request("{{TITRE_DETAIL_DU_REGLEMENT}}", titre_detail_reglement))
    quittance_requests.extend(add_one_request("{{PARAGRAPHE_DETAIL_REGLEMENT_QUITTANCES}}", paragraphe_detail_reglement))

    return quittance_requests
