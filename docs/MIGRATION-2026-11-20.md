# Migrační update — 2026-11-20

Stav production měření na Raspberry Pi po migraci z MicroSD na SSD.
Zdroj: hlášení uživatele Honzicze (Discord thread 1573381326466453565), 20. 11. 2026.
Kompletní skript žije na zařízení v `/srv/speedtest`, ne v tomto repozitáři — tento dokument je kanonický záznam stavu.

## Přechod na SSD

- RPi nyní běží z Kingston SSD na Debianu 13 (arm64). Původní stav: Raspbian 10 buster, armv7l, MicroSD.
- Docker a Dockhand nainstalovány. Home Assistant běží z obrazu `stable`, data obnovena ze zálohy z 16. 11. 2026. ESPHome běží jako čistý stack.
- MicroSD zůstává připojena pouze pro čtení jako rollback; stará verze projektu včetně cronu na ní není nijak změněna.

## Speedtest projekt v /srv/speedtest

- Projekt byl zkopírován z microSD do `/srv/speedtest`; cesty:
  - skript: `/srv/speedtest/src/speedtestdoma.py`
  - Python prostředí: `/srv/speedtest/venv`
  - log: `/srv/speedtest/logs/speedtest.log`
  - Google auth: `/srv/speedtest/config/authgoogle.json`, oprávnění 600 (obsah nikdy do repozitáře)
- Původní Python `speedtest-cli` zůstává nainstalován, pro automatický běh se už nepoužívá.
- Přidán oficiální Ookla CLI 1.2.0.84 pro arm64.
- Cron uživatele `pi`: `0,30 * * * *` (každou hodinu v 00 a 30 minut), výstup do logu výše. Časové pásmo zařízení: `Europe/Prague`.

## Chování měření po úpravě 2026-11-20

`main()` spouští a zapisuje **pouze** měření Ookla CLI proti serveru O2 Czechia, a.s. Praha (ID **30620**). Python knihovna a Quantcom probe jsou z automatického běhu vyřazeny (v kóde `lib = None`, `link = None`). Záloha před úpravou: `speedtestdoma.py.before-ookla-only` (stejná složka).

Opraven převod download/upload z bajtů/s na Mbit/s v `run_cli()`:

```python
"dl": round(d["download"]["bandwidth"] * 8 / 1e6, 2),
"ul": round(d["upload"]["bandwidth"] * 8 / 1e6, 2),
```

**Rozpor k vyřešení (otevřený):** dřívější běhy téhož skriptu dlouhodobě hlásily řádově ~100 Mbit/s (na RPi armv7 i na referenční lane x86 NAS), zatímco aplikace speedtest.net ukazovaly ~690/690. Po opravě převodu hlásí CLI na stejné lince 600–900 Mbit/s. Poměr 8:1 naznačuje, že příčinou starých nízkých čísel mohl být chybějící násobek 8 v převodu, nikoli metodika CLI (four-stream / stableStop). Dokud se nesrovná surový JSON ze zálohy `speedtestdoma.py.before-ookla-only` s aktuálním během, není to bráno jako potvrzená příčina.

Aktuální `main()` na zařízení (výňatek, vložen na základě uživatelského hlášení):

```python
def main():
    cli = run_cli()
    lib = None  # disabled: Ookla CLI is primary
    link = None  # Quantcom probe disabled by request
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    if lib and lib[1] >= LIB_MIN_DL:
        ping = lib[0] if lib[0] is not None else (cli["ping"] if cli else "")
        ul_src = lib[2] if lib[2] >= 50 else (cli["ul"] if cli else lib[2])
        rows.append([ts, ping, lib[1], ul_src, SERVER_BASE + " [dual 16t]",
                     cli["jitter"] if cli else "", cli["loss"] if cli else "", cli["url"] if cli else ""])
        how = "LIB dl=%.0f ul=%.0f%s" % (lib[1], ul_src, "" if lib[2] >= 50 else " (ul z CLI)")
    elif cli:
        rows.append([ts, cli["ping"], cli["dl"], cli["ul"], SERVER_BASE + " [Ookla CLI]",
                     cli["jitter"], cli["loss"], cli["url"]])
        how = "Ookla CLI"
    elif lib:
        rows.append([ts, lib[0], lib[1], lib[2], SERVER_BASE + " [dual 16t]", "", "", ""])
        how = "LIB (cli zablokovana)"
    else:
        rows, how = [], "oba O2 merace selhaly"
    if link:
        rows.append([ts, "", link[0], link[1], LINK_TAG, "", "", ""])
        how += " | LINK dl=%.0f ul=%.0f" % (link[0], link[1])
    if not rows:
        logging.error("Zadna data, bez zapisu.")
        return 1
    try:
        gc = gspread.service_account(filename=AUTH)
        ws = get_worksheet(gc)
        for row in rows:
            ws.append_row(row)
        logging.info("OK %s -> %s (%d radku)" % (how, ts, len(rows)))
        return 0
    except Exception as e:
        logging.error("Zapis: %s" % e)
        return 1
```

## Poslední O2 testy zapsané do Google Sheets (2026-11-20, Europe/Prague)

| Čas | Download (Mbit/s) | Upload (Mbit/s) | Ping (ms) | Jitter (ms) | Ztráta | Výsledková stránka |
|---|---|---|---|---|---|---|
| 17:49:48 | 612,63 | 751,32 | 2,472 | 0,047 | 0 % | https://www.speedtest.net/result/c/ffa58d90-ab67-4ed2-bfc7-fea49fb4a154 |
| 17:51:48 | 917,25 | 742,92 | 2,167 | 0,235 | 0 % | https://www.speedtest.net/result/c/efcdc9fa-c26a-40a7-ade2-a33b055aeadd |

Stav ověření (2026-11-20 z VPS): první výsledek potvrzen přímo na speedtest.net (612,63 / 751,32, server O2 GO Prague, čas sedí). Druhý výsledek jen podle hlášení uživatele — výsledková stránka se z tehdejší sítě nepodařilo vykreslit; odkaz je platný formátově.

## Rollback

- Celé zařízení: restart do MicroSD (původní stav na kartě je nedotčený, včetně cronu a `/home/pi/Speedtest`).
- Samotný skript: `cp /srv/speedtest/src/speedtestdoma.py.before-ookla-only /srv/speedtest/src/speedtestdoma.py` (pouze s explicitním souhlasem uživatele).

## Vztah k tomuto repozitáři

`src/speedtestdoma.py` v repozitáři zůstává původní Python varianta (knihovna `speedtest`). Produkční stav je na zařízení a je popsán zde; zápis 20. 11. 2026 žádný kód do repozitáře nepřepisuje.
