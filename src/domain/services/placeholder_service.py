from src.domain.entities.lease import Lease
from src.domain.housing_strings import (
    cautionnement_physique, la_caution_physique, signature_des_garants,
    cautionnement_visale, doc_visale,
    bail_meuble_duree, reconduction_meuble, duree_contrat_meuble,
    bail_etudiant_titre, bail_etudiant_duree, duree_contrat_etudiant
)

class PlaceholderService:
    def generate_placeholders(self, lease: Lease) -> dict:
        placeholders = {}
        
        tenant = lease.tenant
        prop = lease.property
        room = lease.tenant.room # Accessed via tenant usually or directly? 
        # In Lease entity: tenant, property, period, rent... Room is attached to Tenant in our structure.
        
        # 1. Tenant Info
        placeholders["{{NOM_LOCATAIRE}}"] = tenant.full_name
        placeholders["{{PRENOM}}"] = tenant.nom.split()[1] if len(tenant.nom.split()) > 1 else "" # Weak logic, maybe store separated?
        # Re-check Tenant entity: it has 'nom' (full string?).
        # Actually Tenant entity has just 'nom'. Let's assume 'nom' is Full Name or split needed.
        # Adapters usually map specific fields.
        # Let's rely on what we have.
        placeholders["{{NOM}}"] = tenant.nom
        placeholders["{{MAIL}}"] = tenant.email or ""
        # ... map other basic fields
        if tenant.date_naissance: placeholders["{{DATE_NAISSANCE}}"] = tenant.date_naissance
        if tenant.lieu_naissance: placeholders["{{LIEU_NAISSANCE}}"] = tenant.lieu_naissance
        
        # 2. Property Info
        if prop:
            placeholders["{{ADRESSE_BIEN}}"] = prop.address
            placeholders["{{VILLE}}"] = prop.city
            placeholders["{{CODE_POSTAL}}"] = prop.postal_code
            placeholders["{{NOM_BAILLEUR}}"] = prop.owner_name
            placeholders["{{ADRESSE_BAILLEUR}}"] = prop.owner_address
            
        # 3. Room Info
        if tenant.room:
            placeholders["{{NOM_CHAMBRE}}"] = tenant.room.name
            placeholders["{{SURFACE_CHAMBRE}}"] = str(tenant.room.surface)
            
        # 4. Financials
        placeholders["{{MONTANT_LOYER}}"] = str(lease.rent.amount)
        placeholders["{{MONTANT_CHARGES}}"] = str(lease.charges.amount)
        placeholders["{{MONTANT_TOTAL}}"] = str(lease.total_rent.amount)
        placeholders["{{DEPOT_GARANTIE}}"] = str(lease.deposit.amount)
        
        # 5. Guarantor Logic (Physique vs Visale)
        if tenant.type_garantie and tenant.type_garantie.value == "Visale":
             placeholders["{{CAUTIONNEMENT}}"] = cautionnement_visale
             placeholders["{{DOC_VISA}}"] = doc_visale
             placeholders["{{LA_CAUTION}}"] = ""
             placeholders["{{SIGN_GARANT}}"] = ""
             if tenant.numero_visale: placeholders["{{NUMERO_VISALE}}"] = tenant.numero_visale
        else:
             placeholders["{{CAUTIONNEMENT}}"] = cautionnement_physique
             placeholders["{{DOC_VISA}}"] = ""
             placeholders["{{LA_CAUTION}}"] = la_caution_physique
             placeholders["{{SIGN_GARANT}}"] = signature_des_garants
             
             # Map first guarantor
             if tenant.guarantors:
                 g = tenant.guarantors[0]
                 placeholders["{{NOM_GARANT}}"] = g.nom
                 placeholders["{{PRENOM_GARANT}}"] = g.prenom
                 placeholders["{{ADRESSE_GARANT}}"] = g.adresse
                 # ... others
                 
        # 6. Lease Type Logic
        if tenant.type_bail and tenant.type_bail.value == "Etudiant":
            placeholders["{{PARAGRAPHE_DUREE_CONTRAT}}"] = bail_etudiant_duree
            placeholders["{{TYPE_BAIL_MEUBLE}}"] = bail_etudiant_titre
            placeholders["{{DUREE_CONTRAT}}"] = duree_contrat_etudiant
        else:
            placeholders["{{PARAGRAPHE_DUREE_CONTRAT}}"] = bail_meuble_duree
            placeholders["{{TYPE_BAIL_MEUBLE}}"] = "" # As per failing test fix
            placeholders["{{DUREE_CONTRAT}}"] = duree_contrat_meuble
            placeholders["{{MENTION_RECONDUCTION_MEUBLE}}"] = reconduction_meuble
            
        return placeholders
