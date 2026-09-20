import threading
import time
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock

# Konfigurationswerte aus deiner config.py
from config import TELEGRAM_TOKEN, OPENWEATHER_KEY

# ---------------------------------------------------------
# 1. HINTERGRUND-BOT & WETTER-LOGIK
# ---------------------------------------------------------
def get_weather(city="singen"):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric&lang=de"
        r = requests.get(url, timeout=10).json()
        temp = r["main"]["temp"]
        wind = r["wind"]["speed"]
        desc = r["weather"][0]["description"]
        return f"Wetter in {city.capitalize()}: {temp}°C, {wind} m/s, {desc}"
    except Exception as e:
        return f"Wetter-Fehler: {e}"

def run_bot_background(app_instance):
    """Startet die Hintergrundschleife für den Telegram-Bot."""
    # Aktualisiert den Status auf der Android-Oberfläche
    Clock.schedule_once(lambda dt: app_instance.update_status("🤖 SkyGuardAI Bot aktiv..."))
    
    last_update_id = 0
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN.strip()}/"
    
    while True:
        try:
            # Polling für Telegram-Nachrichten
            res = requests.get(url + f"getUpdates?offset={last_update_id + 1}", timeout=10).json()
            if "result" in res:
                for update in res["result"]:
                    last_update_id = update["update_id"]
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        text = update["message"]["text"].lower()
                        
                        # Befehlsverarbeitung
                        if text == "/start":
                            reply = "🚀 SkyGuard v6 aktiv!"
                        elif "wetter" in text:
                            reply = get_weather("singen")
                        else:
                            reply = "Befehl nicht erkannt. Nutze /start oder wetter."
                            
                        # Antwort senden
                        requests.post(url + "sendMessage", json={"chat_id": chat_id, "text": reply})
        except Exception as e:
            print(f"Bot-Fehler: {e}")
            
        time.sleep(2)

# ---------------------------------------------------------
# 2. KIVY ANDROID GUI
# ---------------------------------------------------------
class SkyGuardUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        self.label_title = Label(
            text="SkyGuardAI", 
            font_size='28sp', 
            bold=True,
            size_hint=(1, 0.3)
        )
        self.label_status = Label(
            text="Starte Dienste...", 
            font_size='18sp',
            size_hint=(1, 0.7)
        )
        
        self.add_widget(self.label_title)
        self.add_widget(self.label_status)

class SkyGuardApp(App):
    def build(self):
        self.ui = SkyGuardUI()
        return self.ui

    def on_start(self):
        # Bot beim App-Start in einem eigenen Thread starten
        threading.Thread(target=run_bot_background, args=(self,), daemon=True).start()

    def update_status(self, text):
        if hasattr(self, 'ui'):
            self.ui.label_status.text = text

if __name__ == '__main__':
    SkyGuardApp().run() 
