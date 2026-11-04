import subprocess

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
        cmd = [
            "yt-dlp",
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
    output_filename = "youtube.m3u"
    m3u_lines = ["#EXTM3U\n"]

    for channel in CHANNELS:
        print(f"Bezig met ophalen verse stream-URL voor {channel['name']} via yt-dlp...")
        stream_url = get_youtube_live_url(channel["url"])
        
        if stream_url:
            print(f"Succes! Gevonden URL: {stream_url}")
            # Bouw de M3U regels op basis van de array-gegevens
            m3u_lines.append(f'#EXTINF:-1 tvg-id="{channel["tvg_id"]}" tvg-logo="{channel["logo"]}" group-title="{channel["group"]}",{channel["name"]}\n')
            m3u_lines.append("#EXTVLCOPT:http-user-agent=Mozilla/5.0\n")
            m3u_lines.append(f"{stream_url}\n")
        else:
            print(f"Fout: Kon geen stream ophalen voor {channel['name']}")

    with open(output_filename, "w", encoding="utf-8") as f:
        f.writelines(m3u_lines)
        
    print(f"Bestand '{output_filename}' is succesvol gegenereerd!")

if __name__ == "__main__":
    main()
