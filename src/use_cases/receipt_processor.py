import os
import re
from datetime import datetime
from src.services.google_doc_and_drive_service import *
from src.conf.info_apis import *
import subprocess 
from subprocess import run, Popen
import time

def run_ahk_script(param1, param2):
    """Run AutoHotkey script with parameters."""
    try:
        ahk_script = "your_script.ahk"  # Replace with your AHK script name
        process = Popen(['AutoHotkey.exe', ahk_script, param1, param2])
        print(f"Started AHK script with parameters: {param1}, {param2}")
        return process
    except Exception as e:
        print(f"Error running AHK script: {str(e)}")
        return None

def parse_receipt_filename(filename):
    """Parse receipt filename to extract relevant information."""
    pattern = r"Quittance--(\d{6})--([^-]+)--(\d+[.,v]?\d*)--(\d+[.,v]?\d*)--(\d+[.,v]?\d*)\.pdf"
    match = re.match(pattern, filename)
    
    if not match:
        return None
        
    month_year = match.group(1)  # MMYYYY
    renter_name = match.group(2).strip()
    amount1 = str(match.group(3).replace("v", ","))
    amount2 = str(match.group(4).replace("v", ","))
    amount3 = str(match.group(5).replace("v", ","))
    
    return {
        'date': month_year,
        'renter_name': renter_name,
        'amount1': amount1,
        'amount2': amount2,
        'amount3': amount3
    }

def process_at_depenses_folder(drive_service, tr_folder_id):
    """Process files in the TR folder."""
    try:
        # Query files in TR folder
        results = drive_service.files().list(
            q=f"'{tr_folder_id}' in parents",
            fields="files(id, name)"
        ).execute()
        
        files = results.get('files', [])
        
        if files:
            print(f"Found {len(files)} file(s) in the TR folder.")
        else:
            print("No files found in the TR folder.")

        for file in files:
            filename = file['name']
            receipt_data = parse_receipt_filename(filename)
            
            if receipt_data:
                # Log extracted parameters
                print(f"Processing file: {filename}")
                print(f"Extracted parameters: {receipt_data}")

                # Call the Puppeteer script with extracted parameters
                puppeteer_script = "puppeter Recording 25_02_2025"
                command = [
                    'node',
                    puppeteer_script,
                    receipt_data['renter_name'],
                    str(receipt_data['amount1']),
                    str(receipt_data['amount2']),
                    str(receipt_data['amount3']),
                    receipt_data['date'],
                    '--wait-after-import',  # Add flag to indicate waiting is needed
                    '--ahk-param1', 'value1',  # Replace with actual parameters
                    '--ahk-param2', 'value2'
                ]
                
                run_puppeteer_script(
                receipt_data['renter_name'],
                receipt_data['amount1'],
                receipt_data['amount2'],
                receipt_data['amount3'],
                receipt_data['date']
                )
            else:
                print(f"⚠️ Skipping file {filename} - doesn't match expected format")
                print("👉 Expected format: Quittance--MMYYYY--NomDuLocataire--Montant1--Montant2--Montant3.pdf")
                print("   Example: Quittance--022025--JohnDoe--300.50--250.00--50.00.pdf\n")
    
    except Exception as e:
        print(f"🔥 Error while processing TR folder: {str(e)}")

def load_receipt_on_website():
    try:
        # Initialize Google Drive service
        drive_service, _, _ = authenticate_and_create_services()
        
        # Find AT and TR folders
        at_folder_id = ID_REPO_DEPENSES_AT
        tr_folder_id = ID_REPO_DEPENSES_TR

        if not all([at_folder_id, tr_folder_id]):
            print("Could not find required folders")
            return
            
        # Process TR folder
        process_at_depenses_folder(drive_service, at_folder_id)
        
    except Exception as e:
        print(f"Error: {str(e)}")


import subprocess

def run_puppeteer_script(renter_name, amount1, amount2, amount3, date):
    """Run Puppeteer script with extracted parameters."""
    try:
        puppeteer_script = r"src\js\Puppeter.js"  # Use raw string for the file path
        command = [
            'node',
            puppeteer_script,
            renter_name,
            str(amount1),
            str(amount2),
            str(amount3),
            date
        ]
        subprocess.run(command, check=True)
        print(f"✅ Puppeteer script executed successfully for {renter_name}")
    except Exception as e:
        print(f"❌ Error running Puppeteer script: {str(e)}")
