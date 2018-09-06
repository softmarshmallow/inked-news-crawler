import json

import boto3

LAMBDA_ENTPOINT_URI = ""
REGION = "ap-northeast-2"

import boto3


ACCESS_ID = "AKIAINK2RVOMOGKLYT7A"
ACCESS_KEY = "CFpVDhMXD+UP3zbwPTWyCvHHXD/Viu6Xr+oA2laC"
client = boto3.client('lambda', region_name='ap-northeast-2', aws_access_key_id=ACCESS_ID,
                      aws_secret_access_key= ACCESS_KEY)

payload = {"url":"https://entertain.naver.com/read?oid=421&aid=0003238897"}


def call_lambda_function():
    invoke_response = client.invoke(
        FunctionName="lambda_function_test",
        InvocationType="RequestResponse",
        Payload=json.dumps(payload)
    )
    data = invoke_response['Payload'].read().decode('utf-8')
    print(type(data))
    json_data = json.loads(data)
    json_data = json.loads(json_data)
    print(type(json_data))
    html = json_data['html']
    print(html)



def main():
    ...

if __name__ == "__main__":
    call_lambda_function()
