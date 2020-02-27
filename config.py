import os
import sys

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CONFIG_ROOT = os.path.join(BASE_DIR, "config")

SERVICE_API_CREDENTIAL = os.path.join(CONFIG_ROOT, "service-api-credential.json")
SERVICE_API_CREDENTIAL_DEV = os.path.join(CONFIG_ROOT, "service-api-credential-development.json")

STAGE = os.getenv('STAGE', 'production')
sys.stdout.writelines(f"stage is {STAGE}\n")
