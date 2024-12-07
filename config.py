from os import getenv
from dotenv import load_dotenv

load_dotenv()

API_ID = int(getenv("API_ID", 0))
API_HASH = getenv("API_HASH")
TOKENS = list(map(str.strip, getenv("TOKENS", None).split(",")))
