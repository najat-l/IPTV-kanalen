import json
import urllib.parse
import urllib.request

# Jouw zenderslijst met de exacte layout-attributen
CHANNELS = [
    {
        "name": "Al Aoula Inter",
        "tvg_id": "AlAoula.ma@Inter",
        "logo": "https://raw.githubusercontent.com/najat-l/IPTV-kanalen/refs/heads/main/Logo's/AlAoula.ma@Inter.png",
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


def generate_snrt_m3u():
  m3u_content = "#EXTM3U\n"
  referrer = "https://snrtlive.ma/"
  user_agent = "Mozilla/5.0"

  for channel in CHANNELS:
    name = channel["name"]
    tvg_id = channel["tvg_id"]
    logo = channel["logo"]
    group = channel["group"]
    raw_url = channel["url"]
    final_stream_url = raw_url

    # Check of het een EasyBroadcast event link is die omgezet moet worden via de API
    if "easybroadcast.io/events/" in raw_url:
      api_url = raw_url.replace(
          "easybroadcast.io/events/", "easybroadcast.io/api/events/"
      )
      try:
        req = urllib.request.Request(
            api_url, headers={"User-Agent": user_agent}
        )
        with urllib.request.urlopen(req) as resp:
          event_data = json.loads(resp.read().decode())
          stream_url = event_data.get("stream") or event_data.get(
              "stream_no_timeshift"
          )

          if stream_url:
            # Vervang playlist_dvr.m3u8 door de werkende chunks_dvr.m3u8 variant met submap indien aanwezig
            if "playlist_dvr.m3u8" in stream_url:
              # Haal de basisstructuur op en pas aan naar chunks
              # Bijv: .../73_aloula_w1dqfwm/playlist_dvr.m3u8 -> .../73_aloula_w1dqfwm/corp/73_aloula_w1dqfwm_480p/chunks_dvr.m3u8
              # We kunnen dit dynamisch afleiden uit de stream_url of direct toevoegen:
              base_path = stream_url.rsplit("/", 1)[0]
              # Extraheer de kanaal-ID uit de URL (bijv. 73_aloula_w1dqfwm)
              parts = stream_url.split("/")
              channel_id = ""
              for p in parts:
                if "_w1dqfwm" in p or "_pgagr52" in p or "_k2tgcj0" in p or "_hthcj4p" in p or "_83tz85q" in p or "_7b7u5n1" in p or "_tccybxt" in p:
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
                # Pas token_path aan naar de chunks-variant als dat nodig is, of behoud de JSON output
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
        print(f"Fout bij verwerken van {name}: {e}")

    # Bouw de regels op exact volgens de layout
    m3u_content += (
        f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{logo}"'
        f' group-title="{group}" http-referrer="{referrer}"'
        f' http-user-agent="{user_agent}",{name}\n'
    )
    m3u_content += f"#EXTVLCOPT:http-referrer={referrer}\n"
    m3u_content += f"#EXTVLCOPT:http-user-agent={user_agent}\n"
    m3u_content += f"{final_stream_url}\n"

  # Schrijf weg naar snrt.m3u
  with open("snrt.m3u", "w", encoding="utf-8") as f:
    f.write(m3u_content)
  print("snrt.m3u succesvol bijgewerkt met de chunks_dvr URL structuur!")


if __name__ == "__main__":
  generate_snrt_m3u()
