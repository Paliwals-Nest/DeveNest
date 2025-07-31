import datetime
import hmac
import base64
import hashlib
import datetime
import hmac
import base64
import hashlib

# Azure DPS details
dps_endpoint = "https://<>dps.azure-devices.net"
primary_key = "R9G4IiolUvmP+4r8G/3+VIEPJgzkH52Mb8YgMCee/q0="

# Define the expiration time for the SAS token (in seconds)
token_ttl = 3600  # Adjust as needed

def generate_sas_token():
    expiry = int((datetime.datetime.utcnow() + datetime.timedelta(seconds=token_ttl)).timestamp())
    resource_uri = f"{dps_endpoint}/enrollments"
    sas_token = generate_sas_token_string(resource_uri, primary_key, expiry)
    return sas_token

def generate_sas_token_string(uri, key, expiry):
    ttl = str(expiry)
    sign_key = f"{uri}\n{ttl}"
    signature = base64.b64encode(
        hmac.new(base64.b64decode(key), msg=sign_key.encode("utf-8"), digestmod=hashlib.sha256).digest()
    )
    signature = signature.decode("utf-8")
    sas_token = f"SharedAccessSignature sr={uri}&sig={signature}&se={ttl}"
    return sas_token

if __name__ == "__main__":
    sas_token = generate_sas_token()
    print(f"Generated SAS Token: {sas_token}")
