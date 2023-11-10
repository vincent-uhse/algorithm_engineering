"""Used to load environment variables"""
import os

import requests
from dotenv import load_dotenv

load_dotenv()

bot_token = os.environ.get("BOT_TOKEN")
chat_id = os.environ.get("CHAT_ID")

if bot_token is None or chat_id is None:
    raise ValueError("Please set the BOT_TOKEN and CHAT_ID environment variables")

MESSAGE_TEXT = "Algorithm analysis results are available!"

url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
params = {"chat_id": chat_id, "text": MESSAGE_TEXT}

response = requests.post(url, params=params, timeout=10)

if response.status_code == 200:
    print("Message sent successfully!")
else:
    print(f"Error sending message. Status code: {response.status_code}")

current_directory = os.getcwd()
url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
params = {"chat_id": chat_id}

for file_name in [
    "visualization_sort_option_1.png",
    "kde_plot_sort_option_1.png",
]:
    files = {"photo": open(current_directory + "/../vis/" + file_name, "rb")}
    response = requests.post(url, params=params, files=files, timeout=10)
    if response.status_code == 200:
        print("Image sent successfully!")
    else:
        print(f"Error sending image. Status code: {response.status_code}")
