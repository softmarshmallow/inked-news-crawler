from config import SERVICE_API_CREDENTIAL
import json

LOCAL_API_MODE = False


if LOCAL_API_MODE:
    BASE_SERVER_URL = "http://localhost:8000/"
    API_KEY = ""
else:
    f = open(SERVICE_API_CREDENTIAL, 'r')
    api_key_data = json.load(f)
    BASE_SERVER_URL = api_key_data['host']
    API_KEY = api_key_data['apikey']

