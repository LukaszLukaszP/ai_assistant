from scripts.config import DEEPSEEK_API_KEY
from scripts.email_service import send_email
from scripts.calendar_service import add_calendar_event
from openai import OpenAI

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

def extract_email_data(prompt: str):
    """ Ekstrakcja danych do e-maila: odbiorca, temat, treść. """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Wyodrębnij odbiorcę, temat i treść wiadomości e-mail."},
                {"role": "user", "content": f"Z podanej wiadomości wyciągnij odbiorcę, temat i treść: {prompt}"}
            ],
            stream=False
        )
        return eval(response.choices[0].message.content)  # Uwaga: DeepSeek zwraca dane jako string słownika!
    except Exception as e:
        return {"recipient": "", "subject": "Brak tematu", "body": prompt}

def extract_event_data(prompt: str):
    """ Ekstrakcja danych do wydarzenia: nazwa, data, godzina. """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Wyodrębnij nazwę, datę i godzinę wydarzenia."},
                {"role": "user", "content": f"Z podanej wiadomości wyciągnij nazwę wydarzenia, datę i godzinę: {prompt}"}
            ],
            stream=False
        )
        return eval(response.choices[0].message.content)
    except Exception as e:
        return {"summary": "Nowe wydarzenie", "start_time": "", "end_time": ""}

def process_intent(prompt: str):
    """ Przetwarza intencję użytkownika i zwraca odpowiednią akcję. """
    result = analyze_intent(prompt)

    if "email" in result:
        email_data = extract_email_data(prompt)
        return {"type": "email", **email_data}
    elif "event" in result:
        event_data = extract_event_data(prompt)
        return {"type": "event", **event_data}
    else:
        return {"type": "chat", "message": prompt}
