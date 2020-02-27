from config import STAGE, SERVICE_API_CREDENTIAL, SERVICE_API_CREDENTIAL_DEV
import json

if STAGE is 'production':
    f = open(SERVICE_API_CREDENTIAL, 'r')
    api_key_data = json.load(f)
    BASE_SERVER_URL = api_key_data['host']
    API_KEY = api_key_data['apikey']
elif STAGE is 'development':
    f = open(SERVICE_API_CREDENTIAL_DEV, 'r')
    api_key_data = json.load(f)
    BASE_SERVER_URL = api_key_data['host']
    API_KEY = api_key_data['apikey']
else:
    BASE_SERVER_URL = "http://localhost:8000/"
    API_KEY = ""
