import os
from dotenv import load_dotenv

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")



CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
