from src.services.google_doc_and_drive_service import *
from src.conf.info_apis import *

def generate_lease_for_tenant(type_caution, drive_service, docs_service, all_replace_requests,formatted_name):
    new_document_name = f"Bail_location_{formatted_name}"

    create_and_export_doc_from_template(
    template_id=ID_TEMPLATE_BAIL_MEUBLE,
    new_document_name=new_document_name,
    replace_requests=all_replace_requests,
    folder_id=ID_REPO_BAUX,
    drive_service=drive_service,
    docs_service=docs_service
    )

    if type_caution == "Physique" :
        new_caution_doc_name = f"Acte_de_caution_solidaire_{formatted_name}"
        create_and_export_doc_from_template(
            template_id=CAUTION_ID,
            new_document_name=new_caution_doc_name,
            replace_requests=all_replace_requests,
            folder_id=ID_REPO_BAUX,
            drive_service=drive_service,
            docs_service=docs_service
        )
