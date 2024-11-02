map_jour = {
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
mois_list = list(map_jour.keys())  # Convertir les clés du dictionnaire en liste