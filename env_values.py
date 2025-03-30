import os
from dotenv import load_dotenv

load_dotenv()

chat_id = os.getenv("CHAT_ID")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
nba_results_api_key = os.getenv("NBA_RESULTS_API_KEY")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"

db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
