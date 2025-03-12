from scripts.email_service import send_email
from scripts.calendar_service import add_calendar_event
from dotenv import load_dotenv
load_dotenv("config/.env")

def test_gmail():
    recipient = "lukasz.test.projekty@gmail.com"  # Podmień na swój testowy e-mail
    subject = "Testowy e-mail od AI Asystenta"
    body = "To jest testowy e-mail wysłany przez Twojego bota!"
    
    result = send_email(recipient, subject, body)
    print("📧 Test Gmail API:", result)

def test_calendar():
    summary = "Testowe spotkanie"
    start_time = "2025-03-13T10:00:00"
    end_time = "2025-03-13T11:00:00"
    
    result = add_calendar_event(summary, start_time, end_time)
    print("📅 Test Google Calendar API:", result)

if __name__ == "__main__":
    print("=== TESTY API GOOGLE ===")
    test_gmail()
    test_calendar()