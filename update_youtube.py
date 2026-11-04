import os
import subprocess

# De zenders die verwerkt moeten worden
CHANNELS = [
    {
        "name": "M24TV",
        "tvg_id": "M24TV.ma",
        "logo": "https://raw.githubusercontent.com/najat-l/IPTV-kanalen/refs/heads/main/Logo's/M24TV.ma.png",
        "group": "News",
        "url": "https://www.youtube.com/watch?v=RgaNtB-sCYU",
    }
]

def get_youtube_live_url(youtube_url):
    try:
        # Haal de raw cookies op uit de environment variable of secret
        raw_cookies = os.environ.get('YOUTUBE_COOKIES', '')
        
        # Bouw een schone Cookie header op basis van de export
        cookie_pairs = []
        for line in raw_cookies.splitlines():
            if line and not line.startswith('#'):
                parts = line.split()
                if len(parts) >= 7:
                    name = parts[5]
                    value = parts[6]
                    cookie_pairs.append(f"{name}={value}")
        
        cookie_header = "; ".join(cookie_pairs)

        cmd = [
            "yt-dlp",
            # Geef de cookies mee als HTTP Header om cookiejar-crashes te omzeilen
            "--add-header", f"Cookie: {cookie_header}",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "-g", 
            youtube_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if result.returncode == 0:
            urls = result.stdout.strip().split('\n')
            if urls and urls[0]:
                return urls[0]
        else:
            print(f"yt-dlp error output: {result.stderr}")
    except Exception as e:
        print(f"Fout bij ophalen YouTube stream voor {youtube_url}: {e}")
    return None

def main():
    m3u_content = "#EXTM3U\n"
    
    for channel in CHANNELS:
        print(f"Bezig met ophalen verse stream-URL voor {channel['name']} via yt-dlp...")
        stream_url = get_youtube_live_url(channel['url'])
        
        if stream_url:
            m3u_content += f"#EXTINF:-1 tvg-id=\"{channel['tvg_id']}\" tvg-logo=\"{channel['logo']}\" group-title=\"{channel['group']}\",{channel['name']}\n"
            m3u_content += f"{stream_url}\n"
            print(f"Succesvolle stream-URL opgehaald voor {channel['name']}")
        else:
            print(f"Fout: Kon geen stream ophalen voor {channel['name']}")

    with open("youtube.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    
    print("Bestand 'youtube.m3u' is succesvol gegenereerd!")

if __name__ == "__main__":
    main()
