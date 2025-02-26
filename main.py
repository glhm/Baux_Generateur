
from src.use_cases.send_receipt_triggered_use_case import *
from src.use_cases.execute_all_tasks_required_by_user import *

from src.use_cases.receipt_processor import *

    # Point d'entrée pour le script
if __name__ == "__main__":
        #do_tasks_required_from_user()
    load_receipt_on_website()    


def lambda_handler(event, context):
    send_receipt_to_tenant(event, context)
