
import os
import boto3
import base64
import json
import requests
from typing import List, Optional
import traceback


from boto3 import Session

from UserMessagesDao import (
    UserMessages,
    get_user_messages
)
from common import (
    get_date_time,
    decode_base64_to_string,
    decode_token
)

um_table_name = os.environ["UMTableName"]

def handler(event, context):
    try:
        body = json.loads(event['body'])
        token = str(body.get('token'))
        print("token:"+token)
        uid = decode_token(token)

        if uid is None:
            return {"statusCode": 500, "body": "Error: Decoded token is None"}

        
       
        boto3_session = boto3.session.Session()
        user_messages = get_user_messages(boto3_session, um_table_name,uid)
        print(user_messages.to_dict())
       
        json_data = {
            'user_messages': user_messages.to_dict()
        }

        return {"statusCode": 200, "body": json.dumps(json_data)}
        
    except Exception as e:
        # 这里捕获所有未预料到的异常，并返回500错误
        print("An unexpected error occurred:", str(e))
        return {"statusCode": 500, "body": "Internal Server Error: " + str(e)}


