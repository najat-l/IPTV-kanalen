import json
import urllib.parse
import urllib.request

# Jouw zenderslijst met de exacte layout-attributen
CHANNELS = [
    {
        "name": "Al Aoula",
        "tvg_id": "AlAoula.ma@SD",
        "logo": "https://raw.githubusercontent.com/najat-l/IPTV-kanalen/refs/heads/main/Logo's/AlAoula.ma.png",
        "group": "General",
        "url": "https://snrt.player.easybroadcast.io/events/73_aloula_w1dqfwm",
    },
    {
        "name": "Al Aoula Laâyoune",
        "tvg_id": "LaayouneTV.ma@SD",
        "logo": "https://raw.githubusercontent.com/najat-l/IPTV-kanalen/refs/heads/main/Logo's/LaayouneTV.ma.png",
        "group": "General",
        "url": "https://snrt.player.easybroadcast.io/events/73_laayoune_pgagr52",
    },
    {
        "name": "Arryadia",
        "tvg_id": "Arryadia.ma@SD",
        "logo": "https://raw.githubusercontent.com/najat-l/IPTV-kanalen/refs/heads/main/Logo's/Arryadia.ma.png",
        "group": "Sports",
        "url": "https://snrt.player.easybroadcast.io/events/73_arryadia_k2tgcj0",
    },
    {
        "name": "Athaqafia",
        "tvg_id": "Athaqafia.ma@SD",
        "logo": "https://raw.githubusercontent.com/najat-l/IPTV-kanalen/refs/heads/main/Logo's/Athaqafia.ma.png",
        "group": "Culture",
        "url": "https://snrt.player.easybroadcast.io/events/73_arrabia_hthcj4p",
    },
    {
        "name": "Al Maghribia",
        "tvg_id": "AlMaghribia.ma@SD",
        "logo": "https://raw.githubusercontent.com/najat-l/IPTV-kanalen/refs/heads/main/Logo's/AlMaghribia.ma.png",
        "group": "General",
        "url": "https://snrt.player.easybroadcast.io/events/73_almaghribia_83tz85q",
    },
    {
        "name": "Assadissa",
        "tvg_id": "Assadissa.ma@SD",
        "logo": "https://raw.githubusercontent.com/najat-l/IPTV-kanalen/refs/heads/main/Logo's/Assadissa.ma.png",
        "group": "Religious",
        "url": "https://snrt.player.easybroadcast.io/events/73_assadissa_7b7u5n1",
    },
    {
        "name": "Aflam TV",
        "tvg_id": "AflamTV.ma@SD",
        "logo": "https://raw.githubusercontent.com/najat-l/IPTV-kanalen/refs/heads/main/Logo's/AflamTV.ma.png",
        "group": "Movies",
        "url": "https://stream-lb.livemediama.com/aflam/hls/stream_3/playlist.m3u8",
    },
    {
        "name": "Tamazight TV",
        "tvg_id": "TamazightTV.ma@SD",
        "logo": "https://raw.githubusercontent.com/najat-l/IPTV-kanalen/refs/heads/main/Logo's/TamazightTV.ma.png",
        "group": "General",
        "url": "https://snrt.player.easybroadcast.io/events/73_tamazight_tccybxt",
    },
]


def fetch_fresh_stream_url(raw_url):
  """Haalt tokens op voor EasyBroadcast URLs en zet ze om naar de werkende chunks URL."""
  user_agent = "Mozilla/5.0"
  final_stream_url = raw_url

  if "easybroadcast.io/events/" in raw_url:
    api_url = raw_url.replace(
        "easybroadcast.io/events/", "easybroadcast.io/api/events/"
    )
    try:
      req = urllib.request.Request(api_url, headers={"User-Agent": user_agent})
      with urllib.request.urlopen(req) as resp:
        event_data = json.loads(resp.read().decode())
        stream_url = event_data.get("stream") or event_data.get(
            "stream_no_timeshift"
        )

        if stream_url:
          if "playlist_dvr.m3u8" in stream_url:
            base_path = stream_url.rsplit("/", 1)[0]
            parts = stream_url.split("/")
            channel_id = ""
            for p in parts:
              if any(
                  sub in p
                  for sub in [
                      "_w1dqfwm",
                      "_pgagr52",
                      "_k2tgcj0",
                      "_hthcj4p",
                      "_83tz85q",
                      "_7b7u5n1",
                      "_tccybxt",
                  ]
              ):
                channel_id = p
                break

            if channel_id:
              stream_url = f"{base_path}/corp/{channel_id}_480p/chunks_dvr.m3u8"

          token_api_url = f"https://token.easybroadcast.io/all?url={urllib.parse.quote(stream_url)}"
          token_req = urllib.request.Request(
              token_api_url, headers={"User-Agent": user_agent}
          )

          with urllib.request.urlopen(token_req) as token_resp:
            token_raw = token_resp.read().decode()
            try:
              token_json = json.loads(token_raw)
              t = token_json.get("token")
              tp = token_json.get("token_path", "%2Fapi%2Fevents")
              exp = token_json.get("expires")
              if t:
                token_query = f"token={t}&expires={exp}&token_path={tp}"
              else:
                token_query = token_raw
            except json.JSONDecodeError:
              token_query = token_raw

            separator = "&" if "?" in stream_url else "?"
            final_stream_url = f"{stream_url}{separator}{token_query}"
    except Exception as e:
      print(f"Fout bij ophalen stream voor {raw_url}: {e}")

  return final_stream_url


def update_playlist():
  input_filename = "IPTV kanalen2.m3u"
  output_filename = "IPTV kanalen2.m3u"

  # Stap 1: Genereer verse URLs en tokens voor alle kanalen in CHANNELS op basis van tvg-id
  updated_channels = {}
  for channel in CHANNELS:
    fresh_url = fetch_fresh_stream_url(channel["url"])
    updated_channels[channel["tvg_id"]] = fresh_url

  # Stap 2: Lees het bestaande M3U-bestand regel voor regel uit
  try:
    with open(input_filename, "r", encoding="utf-8") as f:
      lines = f.readlines()
  except FileNotFoundError:
    print(f"Bestand {input_filename} niet gevonden!")
    return

  new_lines = []
  i = 0
  while i < len(lines):
    line = lines[i]

    # Zoek naar een #EXTINF regel om te kijken of hier een bekende tvg-id in staat
    if line.startswith("#EXTINF:"):
      matched_tvg_id = None
      for tvg_id in updated_channels.keys():
        if f'tvg-id="{tvg_id}"' in line:
          matched_tvg_id = tvg_id
          break

      if matched_tvg_id:
        # Dit kanaal moet bijgewerkt worden!
        new_lines.append(line)  # Behoud de originele #EXTINF regel
        
        # Sla eventuele oude optie-regels (#EXTVLCOPT) direct na #EXTINF over tot we bij de URL zijn
        i += 1
        while i < len(lines) and lines[i].startswith("#EXTVLCOPT:"):
          i += 1  # Overslaan, zodat we de oude stream-URL/opties vervangen

        # Voeg de eventuele VLC opties toe (indien gewenst) of schrijf direct de nieuwe verse URL
        # We halen de verse URL op uit ons dictionary
        new_url = updated_channels[matched_tvg_id]
        new_lines.append(f"{new_url}\n")
        
        # Zoek in de originele lijst of er na de URL nog lege regels stonden en sla de oude URL over
        while i < len(lines) and not lines[i].startswith("#EXTINF") and not lines[i].startswith("# ———") and lines[i].strip() != "" and "http" in lines[i]:
          i += 1
        continue

    # Als het geen gematcht kanaal is, behouden we de regel exact zoals die is
    new_lines.append(line)
    i += 1

  # Stap 3: Schrijf het bijgewerkte bestand weer weg
  with open(output_filename, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

  print(
      f"Bestand '{output_filename}' succesvol bijgewerkt op basis van tvg-id"
      " met behoud van volgorde!"
  )


if __name__ == "__main__":
  update_playlist()