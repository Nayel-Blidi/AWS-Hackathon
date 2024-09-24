import os, sys
from dotenv import load_dotenv

MAIN_DIR = os.path.dirname(__file__)
load_dotenv(dotenv_path=os.path.join(MAIN_DIR, ".env"), override=True)

# IF YOU ARE NOT USING A .env FILE                  #
# MAKE SURE TO REPLACE THESE WITH PLAIN TEXT VALUES #
# OR TO UPDATE THE .env WITH .env_sample FIELDS     #
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")

# This will be shared in the .env file
KNOWLEDGE_BASE_ID = os.getenv("KNOWLEDGE_BASE_ID")