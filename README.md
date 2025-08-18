# Speedtest
### Projekt pro měření rychlosti internetu a ukládání do Google Sheet

## Jak spustit
1. Nainstalujte závislosti: `pip install -r requirements.txt`
2. Konfigurujte soubor `config/config.json`
3. Spusťte skript: `python3 src/main.py`

README: Nasazení skriptu SpeedTest na Raspberry Pi
Tento dokument obsahuje veškeré kroky potřebné pro nasazení a spuštění skriptu pro automatické měření rychlosti internetu a ukládání výsledků do Google Sheetu.

1. Příprava systému a instalace Pythonu
Nejprve se ujisti, že máš nainstalovaný Raspberry Pi OS (64-bit). 64bitová verze je doporučená pro lepší výkon.

Spusť aktualizaci systému:

Bash

sudo apt update && sudo apt full-upgrade -y
Nainstaluj pip a python-venv pro správu balíčků a virtuálních prostředí:

Bash

sudo apt install python3-pip python3-venv -y
2. Klonování projektu a příprava prostředí
Naklonuj projekt z repozitáře a vytvoř virtuální prostředí.

Přejdi do domovského adresáře:

Bash

cd ~
Naklonuj projekt ze svého repozitáře (předpokládáme, že tam je, pokud ne, vytvoř ho ručně):

Bash

git clone https://github.com/tve-uzivatelske-jmeno/tvuj-projekt.git Speedtest
cd Speedtest
Vytvoř a aktivuj virtuální prostředí:

Bash

python3 -m venv venv
source venv/bin/activate
Nainstaluj všechny potřebné balíčky.

Bash

pip install gspread==5.10.0 speedtest-cli oauth2client
(Poznámka: Používáme gspread==5.10.0 kvůli kompatibilitě s Pythonem 3.7 na RPi OS Lite 32-bit).

3. Konfigurace Google Sheets
Pro komunikaci s Google Sheets je potřeba servisní účet.

Vytvoř servisní účet v Google Cloud Console. Vygeneruj a stáhni klíč ve formátu JSON.

Pojmenuj soubor authgoogle.json a ulož ho do adresáře /home/pi/Speedtest/config/.

Oprávnění ke Google Sheetu: Otevři Google Sheet, kam se data ukládají, a sdílej ho se servisním účtem (e-mailová adresa je v JSON souboru, např. muj-ucet@projekt-1234.iam.gserviceaccount.com). Uděl mu oprávnění "Editor".

4. Automatizace spouštění (Cron Job)
Skript musí běžet automaticky. Nejlepší volbou je cron.

Otevři editor crontabu:

Bash

crontab -e
Přidej následující řádek pro spouštění skriptu každou 7. minutu v hodině:

Bash

7 * * * * /home/pi/Speedtest/venv/bin/python3 /home/pi/Speedtest/main.py >> /home/pi/logs/speedtest.log 2>&1
(Poznámka: Uprav cesty, pokud se tvůj projekt nachází jinde.)

Upozornění na logování: Pro správné logování je potřeba vytvořit adresář a nastavit oprávnění:

Bash

mkdir -p /home/pi/logs
Tím se zajistí, že cron job bude mít oprávnění k zápisu logů.

5. Ověření funkčnosti
Spusť skript ručně a zkontroluj, zda se data objeví v Google Sheetu a v logu.

Spusť skript s Pythonem z virtuálního prostředí:

Bash

/home/pi/Speedtest/venv/bin/python3 /home/pi/Speedtest/main.py
Zkontroluj log:

Bash

cat /home/pi/logs/speedtest.log
Pokud jsou výsledky v Google Sheetu i v logu, je vše připraveno.
