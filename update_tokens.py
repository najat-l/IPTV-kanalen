import json
import urllib.request

# Configuratie voor de zenders die je wilt bijwerken
# Je kunt hier meerdere zenders aan toevoegen
CHANNELS = [
    {
        "name": "Al Aoula",
        "event_api": "https://snrt.player.easybroadcast.io/api/events/73_aloula_w1dqfwm",
    },
    # Voeg hier eventueel andere zenders toe met hun event_api URL
]


def get_new_stream_url(event_api_url):
  try:
    # Stap 1: Haal de event data op
    req = urllib.request.Request(
        event_api_url, headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req) as response:
      data = json.loads(response.read().decode())

      # Zoek de stream URL (bijv. "stream" of "stream_no_timeshift")
      stream_url = data.get("stream") or data.get("stream_no_timeshift")
      if not stream_url:
        print(f"Geen stream URL gevonden in {event_api_url}")
        return None

      # Stap 2: Vraag het token op via de token API
      token_api_url = (
          f"https://token.easybroadcast.io/all?url={urllib.parse.quote(stream_url)}"
      )
      token_req = urllib.request.Request(
          token_api_url, headers={"User-Agent": "Mozilla/5.0"}
      )

      with urllib.request.urlopen(token_req) as token_response:
        token_data = json.loads(token_response.read().decode())
        token = token_data.get("token")

        if token and stream_url:
          # Stap 3: Combineer de URL en het token zoals je beschreef
          # Controleer of de URL al parameters heeft of voeg het token toe
          separator = "&" if "?" in stream_url else "?"
          final_url = f"{stream_url}{separator}token={token}"  # Pas aan indien de token-structuur anders verwacht wordt (bijv. &{token})
          return final_url

  except Exception as e:
    print(f"Fout bij ophalen van token voor {event_api_url}: {e}")

  return None


def update_m3u_file():
  m3u_filename = "IPTV kanalen.m3u"

  try:
    with open(m3u_filename, "r", encoding="utf-8") as f:
      content = f.read()

    # Hier kun je logica toevoegen om de regels in je .m3u te zoeken en te vervangen
    # Bijvoorbeeld op basis van de kanaalnaam of een specifiek kenmerk in je m3u.
    print("M3U bestand succesvol ingelezen.")

    # Voorbeeld: Als je een mechanisme hebt om de URL te updaten, schrijf je het hier terug:
    # with open(m3u_filename, "w", encoding="utf-8") as f:
    #     f.write(new_content)

  except FileNotFoundError:
    print(f"Bestand {m3u_filename} niet gevonden in de repository.")


if __name__ == "__main__":
  update_m3u_file()