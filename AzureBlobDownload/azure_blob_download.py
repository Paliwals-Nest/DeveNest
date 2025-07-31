import datetime
import hashlib
import hmac
import base64
import time

import requests
import sys

print("=" *200)
print("list of args")
print(sys.argv[1:])
print("=" *200)

if not sys.argv[1:]:
    print("Sample Usage : "+sys.argv[0]+" <account_name> <blob_storage_url> <container_name> <image_name> <shared_key> "
                                        "<iteration <min 1>>")
    exit()

# Read the arguments from the user.
try:
    account_name = sys.argv[1]
    blob_storage_url = sys.argv[2]
    container_name = sys.argv[3]
    image_name = sys.argv[4]
    shared_key = sys.argv[5]
    iteration = int(sys.argv[6])

    # print(account_name,blob_storage_url,container_name,image_name)

except Exception as e:
    print("Please check no of arguments.")
#     exit()

# account_name = ''
# blob_storage_url = ''
# container_name = ''
# image_name = ''
# shared_key = ''
# iteration = 1


for i in range(0,iteration):

    # Create the url
    url = "https://{0}.{1}/{2}/{3}".format(account_name,blob_storage_url,container_name,image_name)
    print(url)
    request_time = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

    print(request_time)
    time.sleep(2)

    # Create the headers as per microsoft guidelines for shared access key
    # https://docs.microsoft.com/en-us/rest/api/storageservices/authorize-with-shared-key
    string_params = {
            'verb': 'GET',
            'Content-Encoding': '',
            'Content-Language': '',
            'Content-Length': '',
            'Content-MD5': '',
            'Content-Type': '',
            'Date': '',
            'If-Modified-Since': '',
            'If-Match': '',
            'If-None-Match': '',
            'If-Unmodified-Since': '',
            'Range': 'bytes=0-511',
            # 'x-ms-range' : 'bytes=0-511',
            'CanonicalizedHeaders': 'x-ms-date:' + request_time + '\nx-ms-version:' + '2020-04-08' + '\n',
            'CanonicalizedResource': '/' + 'sids' + '/' + container_name + '/' + image_name
        }

    string_to_sign = (string_params['verb'] + '\n'
                          + string_params['Content-Encoding'] + '\n'
                          + string_params['Content-Language'] + '\n'
                          + string_params['Content-Length'] + '\n'
                          + string_params['Content-MD5'] + '\n'
                          + string_params['Content-Type'] + '\n'
                          + string_params['Date'] + '\n'
                          + string_params['If-Modified-Since'] + '\n'
                          + string_params['If-Match'] + '\n'
                          + string_params['If-None-Match'] + '\n'
                          + string_params['If-Unmodified-Since'] + '\n'
                          + string_params['Range'] + '\n'
                          # + string_params['x-ms-range'] + '\n'
                          + string_params['CanonicalizedHeaders']
                          + string_params['CanonicalizedResource'])

    print("="*200)
    print("String to sign")
    print(string_to_sign)
    print("="*200)

    signed_string = base64.b64encode(
            hmac.new(base64.b64decode(shared_key), msg=string_to_sign.encode('utf-8'),
                     digestmod=hashlib.sha256).digest()).decode()

    headers = {
            #'bytes' : '0-511',
            'x-ms-date': request_time,
            'x-ms-version': '2020-04-08',
            'Authorization': 'SharedKey ' + account_name + ':' + signed_string,
            'Range': 'bytes=0-511',
            # 'x-ms-range': 'bytes=0-511'
            #'Range': 'bytes=0-111'
     }

    print("="*200)
    print("\n")
    print("Request Headers::")
    print(headers)
    print("\n")
    print("Downloading the file from azure...")

    # Make a 'GET' call and print status code and headers.

    try:
        data = requests.get(url=url,headers=headers,verify=False)
        print(data.text)

    except Exception as e:
        print("Exception during get call :: " +str(e))
        exit()

    try:
        with open(image_name,'wb') as binary_file:
            binary_file.write(data.content)

        print("="*200)
        print("\n")
        print("Response Headers ::")
        print(data.headers)
        print("\n")
        print("="*200)
    except Exception as e:
        print("Not able to write the file. Exception  ::: " +str(e))
        exit()

    print("Download Done..")



