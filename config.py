import os


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CONFIG_ROOT = os.path.join(BASE_DIR, "config")

SERVICE_API_CREDENTIAL = os.path.join(CONFIG_ROOT, "service-api-credential.json")
