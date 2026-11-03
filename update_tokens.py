import json
import urllib.parse
import urllib.request

# Jouw opgegeven zenderslijst
CHANNELS = [
    {
        "name": "Al Aoula",
        "image": "images/AlAoula.png",
        "url": "https://snrt.player.easybroadcast.io/events/73_aloula_w1dqfwm",
    },
    {
        "name": "Al Aoula Laâyoune",
        "image": "images/LaayouneTV.png",
        "url": "https://snrt.player.easybroadcast.io/events/73_laayoune_pgagr52",
    },
    {
        "name": "Arryadia",
        "image": "images/Arryadia.png",
        "url": "https://snrt.player.easybroadcast.io/events/73_arryadia_k2tgcj0",
    },
    {
        "name": "Athaqafia",
        "image": "images/Athaqafia.png",
        "url": "https://snrt.player.easybroadcast.io/events/73_arrabia_hthcj4p",
    },
    {
        "name": "Al Maghribia",
        "image": "images/AlMaghribia.png",
        "url": "https://snrt.player.easybroadcast.io/events/73_almaghribia_83tz85q",
    },
    {
        "name": "Assadissa",
        "image": "images/Assadissa.png",
        "url": "https://snrt.player.easybroadcast.io/events/73_assadissa_7b7u5n1",
    },
    {
        "name": "Aflam TV",
        "image": "images/AflamTV.png",
        "url": "https://stream-lb.livemediama.com/aflam/hls/stream_3/playlist.m3u8",
    },
    {
        "name": "Tamazight TV",
        "image": "images/TamazightTV.png",
        "url": "https://snrt.player.easybroadcast.io/events/73_tamazight_tccybxt",
    },
]


def generate_snrt_m3u():
  m3u_content = "#EXTM3U\n"

  for channel in CHANNELS:
    name = channel["name"]
    image = channel["image"]
    raw_url = channel["url"]
    final_stream_url = raw_url

    # Check of het een EasyBroadcast event link is die omgezet moet worden via de API
    if "easybroadcast.io/events/" in raw_url:
      # Voeg /api/ toe aan de URL zoals besproken
      api_url = raw_url.replace(
          "easybroadcast.io/events/", "easybroadcast.io/api/events/"
      )
      try:
        # Stap A: Haal de stream URL op uit de event endpoint
        req = urllib.request.Request(
            api_url, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req) as resp:
          event_data = json.loads(resp.read().decode())
          stream_url = event_data.get("stream") or event_data.get(
              "stream_no_timeshift"
          )

          if stream_url:
            # Stap B: Vraag het token op via de token endpoint
            token_api_url = f"https://token.easybroadcast.io/all?url={urllib.parse.quote(stream_url)}"
            token_req = urllib.request.Request(
                token_api_url, headers={"User-Agent": "Mozilla/5.0"}
            )

            with urllib.request.urlopen(token_req) as token_resp:
              token_raw = token_resp.read().decode()
              try:
                token_json = json.loads(token_raw)
                t = token_json.get("token")
                tp = token_json.get("token_path", "%2Fapi%2Fevents")
                exp = token_json.get("expires")
                if t:
                  token_query = f"token={t}&token_path={tp}&expires={exp}"
                else:
                  token_query = token_raw
              except json.JSONDecodeError:
                token_query = token_raw

              # Stap C: Combineer stream URL en token
              separator = "&" if "?" in stream_url else "?"
              final_stream_url = f"{stream_url}{separator}{token_query}"
      except Exception as e:
        print(f"Fout bij verwerken van {name}: {e}")

    # Voeg toe aan de M3U structuur met logo referentie
    m3u_content += (
        f'#EXTINF:-1 tvg-logo="{image}",{name}\n{final_stream_url}\n'
    )

  # Schrijf weg naar snrt.m3u
  with open("snrt.m3u", "w", encoding="utf-8") as f:
    f.write(m3u_content)
  print("snrt.m3u succesvol aangemaakt en bijgewerkt!")


if __name__ == "__main__":
  generate_snrt_m3u()
