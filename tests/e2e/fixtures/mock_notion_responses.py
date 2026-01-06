"""
Mock Notion API responses for E2E tests.
Contains realistic mock data for all 5 Notion databases.
"""


def get_mock_locataire_physique():
    """Locataire with physical guarantor - generates both bail and acte de caution."""
    return {
        "results": [
            {
                "id": "locataire-physique-id-123",
                "properties": {
                    "{NOM_LOCATAIRE}": {"title": [{"text": {"content": "Dupont Jean"}}]},
                    "{PRENOM}": {"rich_text": [{"text": {"content": "Jean"}}]},
                    "{NOM}": {"rich_text": [{"text": {"content": "Dupont"}}]},
                    "{DATE_NAISSANCE}": {"rich_text": [{"text": {"content": "15/03/1995"}}]},
                    "{LIEU_NAISSANCE}": {"rich_text": [{"text": {"content": "Paris"}}]},
                    "{ADRESSE_LOCATAIRE}": {"rich_text": [{"text": {"content": "123 Rue de la Paix, 75001 Paris"}}]},
                    "{MAIL}": {"rich_text": [{"text": {"content": "jean.dupont@email.com"}}]},
                    "{TEL}": {"rich_text": [{"text": {"content": "06 12 34 56 78"}}]},
                    "{MOIS_ARRIVEE}": {"rich_text": [{"text": {"content": "janvier"}}]},
                    "{JOUR_ARRIVEE}": {"number": 15},
                    "{JOUR_DEPART}": {"number": None},
                    "{MOIS_DEPART}": {"number": None},
                    "{ANNEE_DEPART}": {"number": None},
                    "ANNEES": {"multi_select": [{"name": "2026"}]},
                    "Garantie": {"select": {"name": "Physique"}},
                    "MENTION_SPECIALE_LOYER": {"rich_text": []},
                    "TypeDeBail": {"select": {"name": "Meublé"}},
                    "🪙 Garants": {"relation": [{"id": "garant-physique-id-456"}]},
                    "🏠 Biens": {"relation": [{"id": "bien-id-789"}]},
                    "🛏️ Chambres": {"relation": [{"id": "chambre-id-012"}]},
                    "💲 Loyers": {"relation": [{"id": "loyer-id-345"}]},
                    "Générer le bail": {"checkbox": True},
                    "Générer les quittances": {"checkbox": False},
                    "Envoyer Quittance": {"checkbox": False},
                }
            }
        ]
    }


def get_mock_locataire_visale():
    """Locataire with Visale guarantee - generates only bail (no acte de caution)."""
    return {
        "results": [
            {
                "id": "locataire-visale-id-789",
                "properties": {
                    "{NOM_LOCATAIRE}": {"title": [{"text": {"content": "Martin Marie"}}]},
                    "{PRENOM}": {"rich_text": [{"text": {"content": "Marie"}}]},
                    "{NOM}": {"rich_text": [{"text": {"content": "Martin"}}]},
                    "{DATE_NAISSANCE}": {"rich_text": [{"text": {"content": "22/07/1998"}}]},
                    "{LIEU_NAISSANCE}": {"rich_text": [{"text": {"content": "Lyon"}}]},
                    "{ADRESSE_LOCATAIRE}": {"rich_text": [{"text": {"content": "45 Avenue des Champs, 69001 Lyon"}}]},
                    "{MAIL}": {"rich_text": [{"text": {"content": "marie.martin@email.com"}}]},
                    "{TEL}": {"rich_text": [{"text": {"content": "06 98 76 54 32"}}]},
                    "{MOIS_ARRIVEE}": {"rich_text": [{"text": {"content": "février"}}]},
                    "{JOUR_ARRIVEE}": {"number": 1},
                    "{JOUR_DEPART}": {"number": None},
                    "{MOIS_DEPART}": {"number": None},
                    "{ANNEE_DEPART}": {"number": None},
                    "ANNEES": {"multi_select": [{"name": "2026"}]},
                    "Garantie": {"select": {"name": "Visale"}},
                    "MENTION_SPECIALE_LOYER": {"rich_text": []},
                    "TypeDeBail": {"select": {"name": "Etudiant"}},
                    "🪙 Garants": {"relation": [{"id": "garant-visale-id-999"}]},
                    "🏠 Biens": {"relation": [{"id": "bien-id-789"}]},
                    "🛏️ Chambres": {"relation": [{"id": "chambre-id-012"}]},
                    "💲 Loyers": {"relation": [{"id": "loyer-id-345"}]},
                    "Générer le bail": {"checkbox": True},
                    "Générer les quittances": {"checkbox": False},
                    "Envoyer Quittance": {"checkbox": False},
                }
            }
        ]
    }


def get_mock_bien():
    """Mock property (bien) data."""
    return {
        "results": [
            {
                "id": "bien-id-789",
                "properties": {
                    "{ADRESSE_BIEN}": {"rich_text": [{"text": {"content": "55 Rue Renée Auduc, 94000 Créteil"}}]},
                    "{CODE_POSTAL}": {"rich_text": [{"text": {"content": "94000"}}]},
                    "{VILLE}": {"rich_text": [{"text": {"content": "Créteil"}}]},
                    "{SURFACE_TOTALE}": {"number": 120},
                    "{ANNEE_CONSTRUCTION}": {"number": 1985},
                    "{NOM_BAILLEUR}": {"rich_text": [{"text": {"content": "SCI Immobilière"}}]},
                    "{ADRESSE_BAILLEUR}": {"rich_text": [{"text": {"content": "10 Rue du Commerce, 75015 Paris"}}]},
                }
            }
        ]
    }


def get_mock_chambre():
    """Mock room (chambre) data."""
    return {
        "results": [
            {
                "id": "chambre-id-012",
                "properties": {
                    "{NOM_CHAMBRE}": {"rich_text": [{"text": {"content": "Chambre 1"}}]},
                    "{SURFACE_CHAMBRE}": {"number": 12},
                    "{ETAGE}": {"rich_text": [{"text": {"content": "2ème étage"}}]},
                    "{DESCRIPTION_CHAMBRE}": {"rich_text": [{"text": {"content": "Chambre meublée avec vue sur jardin"}}]},
                }
            }
        ]
    }


def get_mock_garant_physique():
    """Mock physical guarantor data."""
    return {
        "results": [
            {
                "id": "garant-physique-id-456",
                "properties": {
                    "{PRENOM_GARANT}": {"rich_text": [{"text": {"content": "Pierre"}}]},
                    "{NOM_GARANT}": {"rich_text": [{"text": {"content": "Dupont"}}]},
                    "{DATE_NAISSANCE_GARANT}": {"rich_text": [{"text": {"content": "10/05/1965"}}]},
                    "{LIEU_NAISSANCE_GARANT}": {"rich_text": [{"text": {"content": "Marseille"}}]},
                    "{ADRESSE_GARANT}": {"rich_text": [{"text": {"content": "78 Boulevard Haussmann, 75008 Paris"}}]},
                    "{TEL_GARANT}": {"rich_text": [{"text": {"content": "06 11 22 33 44"}}]},
                    "{MAIL_GARANT}": {"rich_text": [{"text": {"content": "pierre.dupont@email.com"}}]},
                }
            }
        ]
    }


def get_mock_garant_visale():
    """Mock Visale guarantor data (minimal info since Visale is an organization)."""
    return {
        "results": [
            {
                "id": "garant-visale-id-999",
                "properties": {
                    "{NUMERO_VISALE}": {"rich_text": [{"text": {"content": "VISALE-2026-123456"}}]},
                }
            }
        ]
    }


def get_mock_loyer():
    """Mock rent (loyer) data."""
    return {
        "results": [
            {
                "id": "loyer-id-345",
                "properties": {
                    "{LOYER_HC}": {"number": 450},
                    "{CHARGES}": {"number": 50},
                    "{LOYER_CC}": {"formula": {"type": "number", "number": 500}},
                    "{DEPOT_GARANTIE}": {"number": 450},
                }
            }
        ]
    }


def get_mock_all_data_physique():
    """Complete mocked data for physical guarantor test case."""
    return {
        "locataire": get_mock_locataire_physique(),
        "bien": get_mock_bien(),
        "chambres": get_mock_chambre(),
        "garants": get_mock_garant_physique(),
        "loyer": get_mock_loyer(),
    }


def get_mock_all_data_visale():
    """Complete mocked data for Visale guarantor test case."""
    return {
        "locataire": get_mock_locataire_visale(),
        "bien": get_mock_bien(),
        "chambres": get_mock_chambre(),
        "garants": get_mock_garant_visale(),
        "loyer": get_mock_loyer(),
    }
