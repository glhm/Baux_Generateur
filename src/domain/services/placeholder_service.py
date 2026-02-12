from src.domain.entities.lease import Lease
from src.domain.entities.guarantor import VisaleGuarantor, PhysicalGuarantor
from src.domain.housing_strings import (
    cautionnement_physique, la_caution_physique, signature_des_garants,
    cautionnement_visale, doc_visale,
    bail_meuble_duree, reconduction_meuble, duree_contrat_meuble,
    bail_etudiant_titre, bail_etudiant_duree, duree_contrat_etudiant
)


MONTHS_FR = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}


class PlaceholderService:
    """Stateless domain service computing placeholders from a Lease aggregate."""

    def compute(self, lease: Lease) -> dict:
        placeholders = {}

        placeholders.update(self._tenant_placeholders(lease))
        placeholders.update(self._property_placeholders(lease))
        placeholders.update(self._room_placeholders(lease))
        placeholders.update(self._financial_placeholders(lease))
        placeholders.update(self._guarantor_placeholders(lease))
        placeholders.update(self._lease_type_placeholders(lease))

        return placeholders

    # ==========================================================
    # Private Builders
    # ==========================================================

    def _tenant_placeholders(self, lease: Lease) -> dict:
        tenant = lease.tenant
        if not tenant:
            return {}

        data = {
            "{{NOM_LOCATAIRE}}": tenant.full_name,
            "{{MAIL}}": tenant.email or "",
            "{{DATE_NAISSANCE}}": tenant.date_naissance,
            "{{LIEU_NAISSANCE}}": tenant.lieu_naissance,
            "{{MENTION_SPECIALE}}": lease.mention_speciale or "",
            "{{DATE_FIN}}": lease.date_fin_theorique or ""
        }

        # Nom / Prénom split
        if tenant.nom:
            parts = tenant.nom.split()
            data["{{NOM}}"] = parts[0] if parts else ""
            data["{{PRENOM}}"] = parts[1] if len(parts) > 1 else ""

        # Date début formatée
        if lease.period and lease.period.start_date:
            sd = lease.period.start_date
            day = str(sd.day)
            month = MONTHS_FR.get(sd.month, "")
            year = str(sd.year)

            data.update({
                "{{JOUR_ARRIVEE}}": day,
                "{{MOIS_ARRIVEE}}": month,
                "{{ANNEE_ARRIVEE}}": year,
                "{{DATE_DEBUT}}": f"{day} {month} {year}"
            })

        return data

    def _property_placeholders(self, lease: Lease) -> dict:
        prop = lease.property
        if not prop:
            return {}

        return {
            "{{ADRESSE_BIEN}}": prop.address,
            "{{NOM_BAILLEUR}}": prop.owner_name,
            "{{ADRESSE_BAILLEUR}}": prop.owner_address,
            "{{SURFACE_HABITABLE}}": prop.surface_habitable,
            "{{VILLE}}": "",
            "{{CODE_POSTAL}}": ""
        }

    def _room_placeholders(self, lease: Lease) -> dict:
        if not lease.room:
            return {}

        return {
            "{{NOM_CHAMBRE}}": lease.room.name,
            "{{SURFACE_CHAMBRE}}": str(lease.room.surface)
        }

    def _financial_placeholders(self, lease: Lease) -> dict:
        fin = lease.financials
        if not fin:
            return {}

        return {
            "{{MONTANT_LOYER}}": str(fin.loyer),
            "{{MONTANT_CHARGES}}": str(fin.charges),
            "{{MONTANT_TOTAL}}": str(fin.loyer_CC),
            "{{DEPOT_GARANTIE}}": str(fin.montant_garanties)
        }

def _guarantor_placeholders(self, lease: Lease) -> dict:
    g = lease.guarantor
    if not g:
        return {}

    if lease.is_visale_guarantor():
        return {
            "{{CAUTIONNEMENT}}": cautionnement_visale,
            "{{DOC_VISA}}": doc_visale,
            "{{LA_CAUTION}}": "",
            "{{SIGN_GARANT}}": "",
            "{{NUMERO_VISALE}}": getattr(g, "numero_visale", "") or ""
        }

    if lease.is_physical_guarantor():
        parts = g.full_name_raw.split()
        return {
            "{{CAUTIONNEMENT}}": cautionnement_physique,
            "{{DOC_VISA}}": "",
            "{{LA_CAUTION}}": la_caution_physique,
            "{{SIGN_GARANT}}": signature_des_garants,
            "{{NOM_GARANT}}": parts[0] if parts else "",
            "{{PRENOM_GARANT}}": " ".join(parts[1:]) if len(parts) > 1 else "",
            "{{ADRESSE_GARANT}}": g.address_raw
        }

    return {}


    def _lease_type_placeholders(self, lease: Lease) -> dict:

        if lease.is_student():
            return {
                "{{PARAGRAPHE_DUREE_CONTRAT}}": bail_etudiant_duree,
                "{{TYPE_BAIL_MEUBLE}}": bail_etudiant_titre,
                "{{DUREE_CONTRAT}}": duree_contrat_etudiant
            }

        return {
            "{{PARAGRAPHE_DUREE_CONTRAT}}": bail_meuble_duree,
            "{{TYPE_BAIL_MEUBLE}}": "",
            "{{DUREE_CONTRAT}}": duree_contrat_meuble,
            "{{MENTION_RECONDUCTION_MEUBLE}}": reconduction_meuble
        }
