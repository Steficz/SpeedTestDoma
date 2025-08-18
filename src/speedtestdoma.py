#!/usr/bin/env python3

import os
import logging
import speedtest
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Konfigurace logování
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Konfigurace Google Sheets a autentizace
# Cesta k JSON souboru s klíči se načte z proměnné prostředí
KEY_FILE_PATH = os.getenv('GOOGLE_KEY_FILE', '/home/pi/Speedtest/config/authgoogle.json')
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE_PATH, SCOPE)
    client = gspread.authorize(creds)
except Exception as e:
    logging.error(f"Chyba při autentizaci Google Sheets: {e}")
    exit(1)

# Název Google Sheet
SHEET_NAME = "SpeedTestDoma"
# Hlavičky pro nový list - přidán sloupec pro server
HEADERS = ["Timestamp", "Ping", "Download", "Upload", "Server"]

def get_or_create_worksheet():
    """Vrátí existující list, nebo vytvoří nový pro aktuální měsíc a rok (formát YYYY-MM)."""
    worksheet_title = datetime.now().strftime("%Y-%m")
    try:
        spreadsheet = client.open(SHEET_NAME)
        worksheet = spreadsheet.worksheet(worksheet_title)
        logging.info(f"Používám existující list: '{worksheet_title}'")
        return worksheet
    except gspread.exceptions.WorksheetNotFound:
        logging.warning(f"List '{worksheet_title}' nenalezen, vytvářím nový...")
        spreadsheet = client.open(SHEET_NAME)
        # Změna: přidán sloupec "Server"
        worksheet = spreadsheet.add_worksheet(title=worksheet_title, rows="1", cols="5")
        worksheet.append_row(HEADERS)
        logging.info("Hlavičky byly přidány.")
        return worksheet
    except gspread.exceptions.APIError as e:
        logging.error(f"Chyba při komunikaci s Google API: {e}")
        return None
    except Exception as e:
        logging.error(f"Nepředvídatelná chyba při práci s Google Sheets: {e}")
        return None

def run_speedtest():
    """Provede test rychlosti a vrátí výsledky nebo None v případě chyby."""
    try:
        st = speedtest.Speedtest()
        # Získání informací o nejlepším serveru
        best_server = st.get_best_server()
        st.download()
        st.upload()
        results = st.results.dict()

        download_mbps = round(results['download'] / 1000000, 2)
        upload_mbps = round(results['upload'] / 1000000, 2)
        ping_ms = round(results['ping'], 2)
        
        # Získání názvu serveru a jeho umístění
        server_info = f"{best_server['sponsor']} ({best_server['name']}, {best_server['country']})"
        
        return ping_ms, download_mbps, upload_mbps, server_info
    except speedtest.SpeedtestException as e:
        logging.error(f"Chyba při Speedtestu: {e}")
        return None, None, None, None
    except Exception as e:
        logging.error(f"Neočekávaná chyba při provádění Speedtestu: {e}")
        return None, None, None, None

def main():
    """Hlavní funkce, která orchestrálně volá ostatní."""
    sheet = get_or_create_worksheet()
    if not sheet:
        logging.error("Nelze pokračovat, nepodařilo se získat přístup k listu.")
        return

    ping, download, upload, server_info = run_speedtest()
    if ping is None:
        logging.error("Měření rychlosti selhalo, data nebudou uložena.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Přidání informace o serveru do řádku
    row = [timestamp, ping, download, upload, server_info]

    try:
        sheet.append_row(row)
        logging.info(f"Měření úspěšně uloženo: Ping: {ping}ms, Download: {download}Mbps, Upload: {upload}Mbps, Server: {server_info}")
    except Exception as e:
        logging.error(f"Chyba při zápisu do Google Sheet: {e}")
        
if __name__ == "__main__":
    main()
