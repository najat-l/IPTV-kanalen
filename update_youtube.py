import subprocess

def get_youtube_live_url(youtube_url):
    try:
        # Vraagt de directe stream-url op via yt-dlp
        cmd = ["yt-dlp", "-g", youtube_url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            urls = result.stdout.strip().split('\n')
            if urls:
                return urls[0]
    except Exception as e:
        print(f"Fout bij ophalen YouTube stream voor {youtube_url}: {e}")
    return None

def main():
    youtube_url = "https://www.youtube.com/watch?v=RgaNtB-sCYU"
    print("Bezig met ophalen van live stream URL voor M24 via yt-dlp...")
    
    stream_url = get_youtube_live_url(youtube_url)
    
    if stream_url:
        print(f"Succesvol opgehaald: {stream_url}")
        
        # Schrijf weg naar youtube.m3u
        m3u_content = f"""#EXTM3U
#EXTINF:-1 tvg-id="M24" tvg-name="M24 TV" group-title="News",M24 TV
{stream_url}
"""
        with open("youtube.m3u", "w", encoding="utf-8") as f:
            f.write(m3u_content)
            
        print("Bestand 'youtube.m3u' is succesvol aangemaakt!")
    else:
        print("Fout: Kon geen directe stream URL vinden via yt-dlp.")

if __name__ == "__main__":
    main()
