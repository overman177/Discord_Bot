from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
url = os.getenv('MONGODB_SERVER')
# ===== DATABASE ===========================================================================================================
client = MongoClient(url, server_api=ServerApi('1'))

db = client["discord_bot"]
users_col = db["users"]
camps_col = db["camps"]

# připojení k databázi
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
    print("Chyba připojení k DB -> pravděpodobně nepovolená IP")