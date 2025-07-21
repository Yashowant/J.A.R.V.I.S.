import os
import webbrowser
import requests
import datetime
import random
import subprocess
import smtplib
from email.message import EmailMessage
import imapclient
import pyzmail
import pyautogui
import psutil
from deep_translator import GoogleTranslator
import socket
import json

MEMORY_FILE = "jarvis_memory.json"

API_KEY = ""  # Your OpenRouter API key
MODEL = "deepseek/deepseek-r1-0528:free"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)

def say(text):
    print(f"Jarvis: {text}")

def get_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    say(f"Your IP address is {ip_address}")

def mini_games():
    say("Choose: Guess Number, Rock Paper Scissors, or Math Quiz")
    game = input("Your choice: ").lower()

    if "guess" in game:
        number = random.randint(1, 10)
        say("Guess a number between 1 and 10")
        guess = int(input("Your guess: "))
        if guess == number:
            say("Correct!")
        else:
            say(f"Wrong! The number was {number}")
    
    elif "rock" in game or "paper" in game or "scissors" in game:
        user = input("Rock, Paper, or Scissors: ").lower()
        ai = random.choice(["rock", "paper", "scissors"])
        say(f"I chose {ai}")
        # Add game result logic here

    elif "math" in game:
        a, b = random.randint(1,10), random.randint(1,10)
        say(f"What is {a} + {b}?")
        answer = int(input("Answer: "))
        if answer == a + b:
            say("Correct!")
        else:
            say(f"Wrong! It is {a + b}")

def translate_text():
    sentence = input("Enter sentence to translate: ")
    target_lang = input("Translate to language (e.g., hi, fr, en): ").lower()
    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(sentence)
        say(f"Translated: {translated}")
    except Exception as e:
        say("Translation error.")

def read_inbox():
    try:
        say("Reading Gmail inbox...")

        email_id = "" #Your email id
        app_password = "" #your app password of email id

        imap = imapclient.IMAPClient("imap.gmail.com", ssl=True)
        imap.login(email_id, app_password)
        imap.select_folder("INBOX", readonly=True)

        UIDs = imap.search(['UNSEEN'])[-5:]
        if not UIDs:
            say("No new unread emails.")
            return

        for uid in UIDs:
            raw_msg = imap.fetch([uid], ['BODY[]', 'FLAGS'])
            message = pyzmail.PyzMessage.factory(raw_msg[uid][b'BODY[]'])
            subject = message.get_subject()
            from_email = message.get_addresses('from')[0][1]
            say(f"Email from {from_email}, Subject: {subject}")
            if message.text_part:
                body = message.text_part.get_payload().decode(message.text_part.charset)
                print("Body:", body[:300])
        imap.logout()
    except Exception as e:
        say("Error reading inbox.")

def chat(query):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/yourgithubusername",
        "X-Title": "JarvisAI"
    }

    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are Jarvis, a helpful assistant."},
            {"role": "user", "content": query}
        ]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        result = response.json()
        message = result["choices"][0]["message"]["content"].strip()
        say(message)
        return message
    except Exception as e:
        say("Error during chat.")
        return "Error"

def ai(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/yourusername",
        "X-Title": "JarvisAI"
    }

    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are Jarvis, an intelligent assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        message = result["choices"][0]["message"]["content"]
        say(message)
    except Exception as e:
        say("AI request failed.")

def send_email(to_email, subject, content):
    try:
        from_email = "" #That is also same which in top
        app_password = "" #That is also same which in top

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        msg.set_content(content)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(from_email, app_password)
            smtp.send_message(msg)

        say("Email sent.")
    except Exception as e:
        say("Error sending email.")

def handle_commands(query):
    query = query.lower()

    if "open google" in query:
        search_query = input("What to search on Google: ")
        webbrowser.open(f"https://www.google.com/search?q={search_query}")
        return True

    elif "open calculator" in query:
        subprocess.Popen("calc.exe")
        return True

    elif "open camera" in query:
        os.system("start microsoft.windows.camera:")
        return True

    elif "open explorer" in query:
        os.system("explorer")
        return True

    elif "screenshot" in query:
        screenshot = pyautogui.screenshot()
        screenshot.save("screenshot.png")
        say("Screenshot saved.")
        return True

    elif "system info" in query:
        battery = psutil.sensors_battery()
        cpu_percent = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        say(f"Battery: {battery.percent}%, CPU: {cpu_percent}%, RAM: {ram.percent}%")
        return True

    return False

# ✅ Main Loop
if __name__ == '__main__':
    memory = load_memory()
    say("Jarvis A.I Activated (Text Mode)")
    while True:
        query = input("\nYou: ")

        if not query.strip():
            continue

        if "exit" in query or "quit" in query:
            say("Goodbye!")
            break

        # ✅ ADD MEMORY TRAINING HERE
        if query.startswith("remember that"):
            fact = query.replace("remember that", "").strip()
            key = input("What should I call this memory? (e.g., my birthday, my dog): ").strip()
            memory[key] = fact
            save_memory(memory)
            say(f"Okay, I will remember that '{key}' is '{fact}'")
            continue

        # ✅ ADD MEMORY RECALL HERE
        elif query.startswith("what do you remember about") or "remember" in query:
            key = query.replace("what do you remember about", "").replace("remember", "").strip()
            if key in memory:
                say(f"You told me that {key} is {memory[key]}")
            else:
                say(f"I don't remember anything about {key}")
            continue

        if handle_commands(query):
            continue

        if "open youtube" in query:
            webbrowser.open("https://youtube.com")
        elif "open wikipedia" in query:
            webbrowser.open("https://wikipedia.com")
        elif "time" in query:
            now = datetime.datetime.now().strftime("%H:%M")
            say(f"The time is {now}")
        elif "date" in query:
            today = datetime.date.today()
            say(f"Today's date is {today.strftime('%B %d, %Y')}")
        elif "ip address" in query:
            get_ip()
        elif "internet speed" in query:
            os.system("speedtest")  # requires `speedtest-cli` in your terminal
        elif "send email" in query:
            to = input("To: ")
            subject = input("Subject: ")
            content = input("Message: ")
            send_email(to, subject, content)
        elif "read inbox" in query:
            read_inbox()
        elif "translate" in query:
            translate_text()
        elif "play game" in query:
            mini_games()
        elif "using artificial intelligence" in query:
            ai(prompt=query)
        else:
            chat(query)
