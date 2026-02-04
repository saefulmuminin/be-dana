from dotenv import load_dotenv
import os

load_dotenv()

SIMBA_KEY           = os.getenv("SIMBA_KEY")
SIMBA_ORG           = os.getenv("SIMBA_ORG")
SIMBA_URL           = os.getenv("SIMBA_URL")
API_MUZAKI_REGISTER = SIMBA_URL + os.getenv("API_MUZAKI_REGISTER")
API_MUZAKI_EDIT     = SIMBA_URL + os.getenv("API_MUZAKI_EDIT")

class Config:
    DB_HOST = os.getenv('DB_HOST')
    DB_USER = os.getenv('DB_USER')
    DB_PASS = os.getenv('DB_PASS')
    DB_NAME = os.getenv('DB_NAME')
