import subprocess

# Uruchomienie FastAPI
subprocess.Popen(["uvicorn", "scripts.api:app", "--reload"])

# Uruchomienie bota Telegrama
subprocess.Popen(["python", "scripts/ai_assistant.py"])
