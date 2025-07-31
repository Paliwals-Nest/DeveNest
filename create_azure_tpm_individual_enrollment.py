import requests
import json
import argparse
import hmac
from base64 import b64encode, b64decode
from urllib.parse import quote_plus, urlencode
from time import time
from hashlib import sha256


# Azure AD application credentials
#

KEYS_URL = (
    "https://management.azure.com/subscriptions/{0}/resourceGroups/{1}/providers/Microsoft.Devices/"
    "provisioningServices/{2}/listkeys?api-version=2018-01-22"
)


def generate_sas_token(dps_primary_key, dps_key_name, dps_endpoint, expiry=7200):
    """

    :param dps_primary_key:
    :param dps_key_name:
    :param dps_endpoint:
    :param expiry:
    :return:
    """
    uri = dps_endpoint
    key = dps_primary_key
    policy_name = dps_key_name
    ttl = time() + expiry

    sign_key = "%s\n%d" % ((quote_plus(uri)), int(ttl))

    signature = b64encode(
        hmac.new(b64decode(key), sign_key.encode("utf-8"), sha256).digest()
    )

    rawtoken = {"s1r": uri, "sig": signature, "se": str(int(ttl)), "skn": policy_name}

    print("SharedAccessSignature ::::  " + urlencode(rawtoken))
    print("-" * 10)
    print("-" * 10)
    return "SharedAccessSignature " + urlencode(rawtoken)


def get_dps_keys(token, subscription_id, resource_group, dps_serivce_name):
    """
    Responsible for fetching dps key..
    :return:
    Dps keys
    """

    #
    primary_key, key_name = None, None
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
    }

    keys_url = KEYS_URL.format(subscription_id, resource_group, dps_serivce_name)
    print("keys_url ::" + str(keys_url))

    response = requests.post(keys_url, headers=headers)

    if response.status_code == 200:
        keys_data = response.json()
        print(response.text)
        print("-" * 10)
        print("-" * 10)
        print("DPS Keys:")
        for key in keys_data["value"]:
            print(f"Key Name: {key['keyName']}")
            print(f"Primary Key: {key['primaryKey']}")
            print(f"Secondary Key: {key['secondaryKey']}")
            primary_key = key["primaryKey"]
            key_name = key["keyName"]
        print("-" * 10)
        print("-" * 10)

        if primary_key and key_name:
            return primary_key, key_name
        else:
            print("Primary key and key name not found ::::: " + str(keys_data))
            return None, None
    else:
        print("-" * 10)
        print("-" * 10)
        print(f"Failed to list DPS keys. Status Code: {response.status_code}")
        print(response.text)
        print("-" * 10)
        print("-" * 10)

        return None, None


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

    return token


def create_tpm_individual_enrollment_group(
    client_id,
    client_secret,
    tenant_id,
    dps_service_name,
    endorsement_key,
    registration_id,
    iothub_name,
    subscription_id,
    resource_group,
):
    # Replace with your Azure AD bearer token

    print("Iothub Name ::: " + str(iothub_name))
    print("Dps Name:: " + str(dps_service_name))
    token = get_azure_access_token(client_id, client_secret, tenant_id)
    if token:
        primary_key, key_name = get_dps_keys(
            token, subscription_id, resource_group, dps_service_name
        )

        if primary_key and key_name:
            # Replace with your DPS resource URI
            # dps_resource_uri = f"https://{DPS_SERVICE_NAME}.azure-devices-provisioning.net"

            # Individal Enroll..
            enrollment_individual_data = {
                "attestation": {
                    "type": "tpm",
                    "tpm": {
                        "endorsementKey": endorsement_key,  # Replace with your TPM endorsement key
                    },
                },
                "provisioningStatus": "enabled",
                "allocationPolicy": "hashed",
                "registrationId": registration_id,
                "reprovisionPolicy": {
                    "migrateDeviceData": True,
                    "updateHubAssignment": True,
                },
                # Choose allocation policy as per your requirements
            }

            # Endpoint for creating enrollment group
            sas_token = generate_sas_token(
                primary_key,
                key_name,
                dps_service_name + ".azure-devices-provisioning.net",
            )

            individual_enrollment = f"https://{dps_service_name}.azure-devices-provisioning.net/enrollments/{registration_id}?api-version=2019-03-31"


            print(individual_enrollment)

            # Send the POST request to create the enrollment group
            headers = {
                "Authorization": f"{sas_token}",
                "Content-Type": "application/json",
            }

            print(headers)

            print(json.dumps(enrollment_individual_data))

            response = requests.put(
                individual_enrollment,
                headers=headers,
                data=json.dumps(enrollment_individual_data),
            )

            if response.status_code == 200:
                print("Individual Enrollment Group created successfully.")
                print(response.text)
            else:
                print(
                    f"Failed to create the Individual Enrollment Group. Status code: {response.status_code}, Response: {response.text},"
                )
                print("-" * 10)
                print("-" * 10)


if __name__ == "__main__":
    parse = argparse.ArgumentParser(prog="Create Enrollment Group")
    parse.add_argument("client_id", help="App Id")
    parse.add_argument("tenant_id", help="Tenant id")
    parse.add_argument("client_secret", help="App Password")
    parse.add_argument("dps_service_name", help="Dps Service Name")
    parse.add_argument(
        "endorsement_key",
        help="Endoresement key - fetched from Device -> Basic Info -> Endorsement key ",
    )
    parse.add_argument("iothub_name", help="Name of the iothub")
    parse.add_argument("subscription_id", help="Subscription id")
    parse.add_argument("resource_group", help="name of the resource group")
    parse.add_argument(
        "registration_id",
        help="registration id to be used in creating individual enrollment",
    )

    args = parse.parse_args()

    create_tpm_individual_enrollment_group(
        args.client_id,
        args.client_secret,
        args.tenant_id,
        args.dps_service_name,
        args.endorsement_key,
        args.registration_id,
        args.iothub_name,
        args.subscription_id,
        args.resource_group,
    )










