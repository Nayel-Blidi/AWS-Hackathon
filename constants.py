import os, sys
from dotenv import load_dotenv

MAIN_DIR = os.path.dirname(__file__)
load_dotenv(dotenv_path=os.path.join(MAIN_DIR, ".env"), override=True)

HUGGING_TOKEN = os.getenv("HUGGING_TOKEN")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")
KNOWLEDGE_BASE_ID = os.getenv("KNOWLEDGE_BASE_ID")