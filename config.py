from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID= os.environ.get('TELEGRAM_API', '')
API_HASH = os.environ.get('TELEGRAM_HASH', '')
DUMP_ID = os.environ.get('DUMP_CHAT_ID', '')
COMMUNITY_ID = os.getenv("COMMUNITY_ID")
GROUP_ID = os.getenv("GROUP_ID")