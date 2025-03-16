import sys
import subprocess
import time

# Uruchomienie FastAPI
api_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "scripts.api:app", "--reload"])

# Uruchomienie bota Telegrama (zmienione na telegram_bot)
bot_process = subprocess.Popen([sys.executable, "-m", "scripts.telegram_bot"])

try:
    print("🚀 Agent AI uruchomiony! FastAPI działa na http://127.0.0.1:8000")
    while True:
        time.sleep(1)  # Utrzymuje główny proces przy życiu
except KeyboardInterrupt:
    print("\n🛑 Zatrzymywanie procesu...")
    api_process.terminate()
    bot_process.terminate()
    api_process.wait()
    bot_process.wait()
    print("✅ Procesy zakończone.")
