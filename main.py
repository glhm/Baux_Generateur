
from src.use_cases.execute_all_tasks_required_by_user import *
from src.use_cases.check_for_receipts_to_send import check_for_receipt_to_send


    # Point d'entrée pour le script
if __name__ == "__main__":
    #check_for_receipt_to_send()
    do_tasks_required_from_user()

def lambda_handler(event, context):
    check_for_receipt_to_send()