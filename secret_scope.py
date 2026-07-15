import os
import requests
from dotenv import load_dotenv, find_dotenv

# Lade deine lokalen Zugangsdaten aus der .env
load_dotenv(find_dotenv())
host = os.environ.get("DATABRICKS_HOST")
token = os.environ.get("DATABRICKS_TOKEN")

# API URLs
headers = {"Authorization": f"Bearer {token}"}
scope_name = "secret_scope_VPS"
key_name = "DB-token"

print(f"Verbinde mit {host}...")

# 1. Tresor (Scope) erstellen
url_scope = f"https://{host}/api/2.0/secrets/scopes/create"
res_scope = requests.post(url_scope, headers=headers, json={"scope": scope_name})

if res_scope.status_code == 200:
    print(f"✅ Tresor '{scope_name}' erfolgreich erstellt!")
elif "RESOURCE_ALREADY_EXISTS" in res_scope.text:
    print(f"ℹ️ Tresor '{scope_name}' existiert bereits.")
else:
    print(f"❌ Fehler beim Erstellen des Tresors: {res_scope.text}")

# 2. Passwort in den Tresor legen
url_secret = f"https://{host}/api/2.0/secrets/put"
res_secret = requests.post(url_secret, headers=headers, json={
    "scope": scope_name, 
    "key": key_name, 
    "string_value": token  # Wir legen genau den Token aus deiner .env in den Tresor
})

if res_secret.status_code == 200:
    print(f"✅ Geheimnis '{key_name}' erfolgreich im Tresor hinterlegt!")
else:
    print(f"❌ Fehler beim Speichern des Geheimnisses: {res_secret.text}")
