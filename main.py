import subprocess

# Uruchomienie FastAPI (asynchronicznie)
subprocess.Popen(["uvicorn", "scripts.ai_assistant_api:app", "--reload"])

# Uruchomienie bota Telegrama
subprocess.Popen(["python", "scripts/ai_assistant.py"])