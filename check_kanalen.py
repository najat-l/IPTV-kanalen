import sys
import urllib.request
import urllib.error

INPUT_FILE = "kanalen.m3u"
TIMEOUT = 5  # Seconden per stream-check

def check_channel(url, referrer, user_agent):
    headers = {
        "User-Agent": user_agent or "Mozilla/5.0",
    }
    if referrer:
        headers["Referer"] = referrer

    # Probeer eerst een snelle HEAD-request
    try:
        req = urllib.request.Request(url, headers=headers, method="HEAD")
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            if response.status in (200, 206, 301, 302, 307, 308):
                return True, response.status
    except Exception:
        # Als HEAD faalt (sommige servers ondersteunen dat niet), probeer een kleine GET-request
        try:
            req = urllib.request.Request(url, headers=headers, method="GET")
            # Haal alleen de eerste 1024 bytes op
            req.add_header("Range", "bytes=0-1023")
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                if response.status in (200, 206, 301, 302, 307, 308):
                    return True, response.status
        except urllib.error.HTTPError as e:
            return False, e.code
        except Exception as e:
            return False, str(e)
            
    return False, "Geen respons"

def main():
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Bestand '{INPUT_FILE}' niet gevonden!")
        sys.exit(1)

    channels = []
    current_name = "Onbekend"
    current_referrer = ""
    current_user_agent = ""

    for line in lines:
        line_str = line.strip()
        if line_str.startswith("#EXTINF:"):
            # Haal de kanaalnaam op (staat na de laatste komma)
            if "," in line_str:
                current_name = line_str.rsplit(",", 1)[1]
            else:
                current_name = line_str
                
            # Haal eventuele referrer uit de EXTINF regel
            if 'http-referrer="' in line_str:
                current_referrer = line_str.split('http-referrer="')[1].split('"')[0]
            else:
                current_referrer = ""
                
        elif line_str.startswith("#EXTVLCOPT:http-referrer="):
            current_referrer = line_str.split("=", 1)[1]
        elif line_str.startswith("#EXTVLCOPT:http-user-agent="):
            current_user_agent = line_str.split("=", 1)[1]
        elif line_str.startswith("http://") or line_str.startswith("https://"):
            channels.append({
                "name": current_name,
                "url": line_str,
                "referrer": current_referrer,
                "user_agent": current_user_agent
            })
            # Reset voor het volgende kanaal
            current_name = "Onbekend"
            current_referrer = ""
            current_user_agent = ""

    print(f"--- Gestart met controleren van {len(channels)} kanalen in {INPUT_FILE} ---\n")
    
    online_count = 0
    offline_channels = []

    for idx, ch in enumerate(channels, 1):
        print(f"[{idx}/{len(channels)}] Controleren: {ch['name']}...", end=" ", flush=True)
        is_ok, status = check_channel(ch["url"], ch["referrer"], ch["user_agent"])
        
        if is_ok:
            print(f"OK (Status: {status})")
            online_count += 1
        else:
            print(f"MISLUKT (Fout/Status: {status})")
            offline_channels.append((ch['name'], ch['url'], status))

    print("\n================ SAMENVATTING ================")
    print(f"Totaal kanalen: {len(channels)}")
    print(f"Online: {online_count}")
    print(f"Offline / Verlopen: {len(offline_channels)}")
    
    if offline_channels:
        print("\n--- Lijst met onbereikbare kanalen ---")
        for name, url, err in offline_channels:
            print(f"- {name} | Fout: {err}\n  URL: {url}")
    print("==============================================")

if __name__ == "__main__":
    main()
