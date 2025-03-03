map_mois_to_dernier_jour = {
                "Janvier": 31,
                "Février": 28,  # Attention, février peut être de 28 ou 29 jours selon l'année (non pris en compte ici)
                "Mars": 31,
                "Avril": 30,
                "Mai": 31,
                "Juin": 30,
                "Juillet": 31,
                "Août": 31,
                "Septembre": 30,
                "Octobre": 31,
                "Novembre": 30,
                "Décembre": 31
            }
mois_list = list(map_mois_to_dernier_jour.keys())  # Convertir les clés du dictionnaire en liste

def get_month_index(month_name):
    """
    Obtient l'index d'un mois à partir de son nom.
    
    :param month_name: Nom du mois en français.
    :return: Index du mois (1-12).
    """
    try:
        return mois_list.index(month_name) + 1
    except ValueError:
        raise ValueError(f"Mois non reconnu: {month_name}")
    
def get_dernier_jour_du_mois_par_numero(mois_numero):
    if 1 <= mois_numero <= 12:
        mois_nom = mois_list[mois_numero - 1]  # -1 car les indices commencent à 0
        return map_mois_to_dernier_jour[mois_nom]
    else:
        raise ValueError("Le numéro du mois doit être entre 1 et 12.")



def compare_dates(year1, month_index1, day1, year2, month_index2, day2):
    """
    Compare deux dates et retourne:
    -1 si date1 < date2
     0 si date1 == date2
     1 si date1 > date2
    
    :param year1: Année de la première date.
    :param month_index1: Index du mois de la première date (1-12).
    :param day1: Jour de la première date.
    :param year2: Année de la deuxième date.
    :param month_index2: Index du mois de la deuxième date (1-12).
    :param day2: Jour de la deuxième date.
    :return: -1, 0 ou 1 selon la comparaison.
    """
    if year1 < year2:
        return -1
    elif year1 > year2:
        return 1
    else:  # Même année
        if month_index1 < month_index2:
            return -1
        elif month_index1 > month_index2:
            return 1
        else:  # Même mois
            if day1 < day2:
                return -1
            elif day1 > day2:
                return 1
            else:  # Même jour
                return 0