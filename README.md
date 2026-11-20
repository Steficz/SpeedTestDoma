# SpeedTestDoma

Skript pro měření rychlosti internetu a ukládání výsledků do Google Sheet.

## Kód

`src/speedtestdoma.py` — jeden soubor, čtyři části:

- **Setup (při importu):** logování do stdout; gspread + `oauth2client` servisní účet, cesta ke JSON klíči z env `GOOGLE_KEY_FILE` (výchozí `/home/pi/Speedtest/config/authgoogle.json`), scopes pro Sheets + Drive. Autentizace selže ⇒ skript skončí s chybou.
- **`get_or_create_worksheet()`:** otevře spreadsheet `SpeedTestDoma` a list pojmenovaný podle aktuálního měsíce `YYYY-MM`. Když list neexistuje, vytvoří ho (5 sloupců) a zapíše hlavičky `Timestamp, Ping, Download, Upload, Server`.
- **`run_speedtest()`:** Python knihovna `speedtest` (speedtest-cli): `get_best_server()` (nejmenší ping), `download()`, `upload()`. Z `results.dict()` vydá ping a rychlosti v Mbit/s (dělení `1e6`) a popis serveru `sponsor (name, country)`. Při výjimce vrátí samé `None`.
- **`main()`:** získá list → změří → připojí řádek `[timestamp, ping, download, upload, server]` přes `append_row`. Selhání měření i zápisu se jen loguje, řádek se nevloží.

## Závislosti

`speedtest-cli`, `gspread`, `oauth2client` (v repozitáři je `requirements.txt` prázdný).

## Spuštění

```sh
python3 -m venv venv
venv/bin/pip install speedtest-cli gspread oauth2client
GOOGLE_KEY_FILE=/cesta/authgoogle.json venv/bin/python3 src/speedtestdoma.py
```

Servisní účet z JSON musí mít na listu oprávnění Editor. `authgoogle.json` nepatží do repozitáře (mimo jiné proto `config/` v repozitáři chybí).

## Produkce

Produkční běžec je přepsaná varianta používající oficiální Ookla CLI, nasazená na Raspberry Pi v `/srv/speedtest` (cron `0,30 * * * *`); její stav, jednotkový převod a rollback popisuje [docs/MIGRATION-2026-11-20.md](docs/MIGRATION-2026-11-20.md).
