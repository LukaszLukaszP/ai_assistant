from scripts.config import DEEPSEEK_API_KEY
from scripts.email_service import send_email
from scripts.calendar_service import add_calendar_event
from openai import OpenAI

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def analyze_intent(prompt: str):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Jesteś inteligentnym asystentem. Masz zwrócić TYLKO jedno słowo: "
                        "'email', 'event' albo 'chat'. Żadnych wyjaśnień. "
                        "Decyduj na podstawie wiadomości użytkownika."
                    )
                },
                {
                    "role": "user",
                    "content": f"Czy ta wiadomość to email, event czy chat? {prompt}"
                }
            ],
            stream=False
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        return "chat"


def extract_email_data(prompt: str):
    """
    Wyodrębnij adres e-mail z wiadomości użytkownika
    ORAZ na podstawie kontekstu (promptu) wygeneruj własny temat i treść wiadomości.
    Zwróć słownik Python w formacie:
    {
      'recipient': 'lukasz.test.projekty@gmail.com',
      'subject': 'Wygenerowany temat',
      'body': 'Wygenerowana treść'
    }
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Twoje zadanie:\n"
                        "1) Wyodrębnij ADRES ODBIORCY (recipient) z wiadomości użytkownika, jeśli występuje.\n"
                        "2) Na podstawie kontekstu wiadomości (promptu) SAM stwórz odpowiedni TEMAT (subject)\n"
                        "   i TREŚĆ (body) wiadomości e-mail.\n\n"
                        "Zwróć wynik WYŁĄCZNIE jako słownik Python w formacie:\n"
                        "{'recipient': 'adres@example.com', 'subject': 'Wygenerowany temat', 'body': 'Wygenerowana treść'}\n"
                        "Nie dodawaj żadnych komentarzy ani wyjaśnień, tylko i wyłącznie taki słownik.\n"
                        "Jeśli nie znajdujesz jakiegoś elementu, użyj pustego stringa."
                    )
                },
                {
                    "role": "user",
                    "content": f"{prompt}"
                }
            ],
            stream=False
        )

        raw_content = response.choices[0].message.content
        print("DEBUG extract_email_data - surowa odpowiedź:\n", raw_content)

        # Zakładamy, że model zwraca wyłącznie słownik w formacie Python
        return eval(raw_content)

    except Exception as e:
        print("extract_email_data - wyjątek:", e)
        # Jeśli coś pójdzie nie tak, zwracamy fallback
        return {
            "recipient": "",
            "subject": "Brak tematu",
            "body": prompt
        }


def extract_event_data(prompt: str):
    """ Ekstrakcja danych do wydarzenia: nazwa, data rozpoczęcia i zakończenia.
        Format daty musi być zgodny z RFC3339, np.: '2023-03-15T10:00:00+02:00'
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Twoje zadanie: Wyodrębnij z podanej wiadomości nazwę wydarzenia, "
                        "datę rozpoczęcia i zakończenia w formacie RFC3339 (np. '2023-03-15T10:00:00+02:00').\n"
                        "Zwróć wynik WYŁĄCZNIE jako słownik Python w następującym formacie:\n"
                        "{'summary': 'Nazwa wydarzenia', 'start_time': 'Data rozpoczęcia', 'end_time': 'Data zakończenia'}\n"
                        "Nie dodawaj żadnych dodatkowych komentarzy ani tekstu."
                    )
                },
                {
                    "role": "user",
                    "content": f"Z podanej wiadomości wyciągnij nazwę wydarzenia, datę rozpoczęcia i zakończenia: {prompt}"
                }
            ],
            stream=False
        )
        raw_content = response.choices[0].message.content
        print("DEBUG extract_event_data - surowa odpowiedź:\n", raw_content)
        return eval(raw_content)
    except Exception as e:
        print("extract_event_data - wyjątek:", e)
        return {"summary": "Nowe wydarzenie", "start_time": "", "end_time": ""}

def process_intent(prompt: str):
    prompt_lower = prompt.lower()

    # Ręcznie wymuszaj "email", jeśli widzisz frazę "wyślij maila"
    if "wyślij maila" in prompt_lower or "wyślij email" in prompt_lower:
        email_data = extract_email_data(prompt)
        return {"type": "email", **email_data}
    
    """ Przetwarza intencję użytkownika i zwraca odpowiednią akcję. """
    result = analyze_intent(prompt)
    print("DEBUG analyze_intent =", result)  # <-- Dodaj to

    if "email" in result:
        email_data = extract_email_data(prompt)
        return {"type": "email", **email_data}
    elif "event" in result:
        event_data = extract_event_data(prompt)
        return {"type": "event", **event_data}
    else:
        return {"type": "chat", "message": prompt}

def chat_with_deepseek(prompt: str) -> str:
    """
    Wysyła zapytanie do modelu DeepSeek i zwraca gotową odpowiedź tekstową.
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Jesteś inteligentnym asystentem, który odpowiada na pytania."},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Przepraszam, wystąpił błąd: {e}"