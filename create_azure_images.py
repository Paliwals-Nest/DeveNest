import json

import requests


IMAGE_URL = (
"https://management.azure.com/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Compute/images/Img_eve1?api-version=2023-07-01"
)


def get_azure_access_token(client_id, client_secret, tenant_id):
    """
    Responsible for fetching the access token
    :param client_id:
    Id of the app
    :param client_secret:
    Pass/secrect for the app
    :param tenant_id:
    Id of the tenant
    :return:
    """

    # Azure AD OAuth 2.0 token endpoint
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"

    # Request parameters
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "resource": "https://management.azure.com/",  # Replace with the appropriate DPS resource URI
    }

    try:
        response = requests.post(token_url, data=data)
        token = response.json().get("access_token")
    except Exception as e:
        print("Response while fetching token : :::" + str(response.status_code))
        print("Exceptions while fetching token  :::: " + str(e))
        return None

    print(token)
    return token


def create_images(token, subscription_id, resource_group):
    """

    """

    #
    primary_key, key_name = None, None
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
    }

    keys_url = IMAGE_URL.format(subscription_id, resource_group)
    print("keys_url ::" + str(keys_url))

    data = {
  "location": "centralindia",
    "properties": {
    "storageProfile": {
      "osDisk": {
        "osType": "Linux",
        "diskSizeGB": 10,
        "caching": "ReadWrite",
        "storageAccountType": "StandardSSD_LRS",
        "blobUri": "https://sidblobs.blob.core.windows.net/images/azureeve.vhd",
        "osState": "Specialized",

    },
       "dataDisks": [],
      "zoneResilient": True
    },
      "hyperVGeneration": "V1"
  }
}

    response = requests.put(keys_url, headers=headers,data=json.dumps(data))
    print(response.text)


# def create_vm()


if __name__ == '__main__':
    token = get_azure_access_token('','','')
    create_images(token, '' ,'')







