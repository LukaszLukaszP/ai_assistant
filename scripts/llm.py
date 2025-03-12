from openai import OpenAI
from scripts.config import DEEPSEEK_API_KEY

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def analyze_intent(prompt: str):
    """
    Analizuje wiadomość użytkownika i klasyfikuje, czy to:
    - Normalna rozmowa → "chat"
    - Wysłanie e-maila → "email"
    - Dodanie wydarzenia → "event"
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Jesteś inteligentnym asystentem, który analizuje polecenia użytkownika."},
                {"role": "user", "content": f"Czy ta wiadomość to e-mail, wydarzenie czy zwykła rozmowa? {prompt}"}
            ],
            stream=False
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        return "chat"  # Domyślnie chatbot, jeśli coś pójdzie nie tak
