
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

table_name = os.environ["TableName"]

def handler(event, context):
    try:
        bodyStr = event["body"]
        bodyJson = decode_base64_to_string(bodyStr)
        body = json.loads(bodyJson)
        print("body:"+str(body))
        token = str(body.get('token'))
        connection_id = str(body.get('connection_id'))
        logMessageIdList = str(body.get('logMessageIdList'))

        uid = decode_token(token)
        if uid is None:
            return {"statusCode": 500, "body": "Error: Decoded token is None"}

        data = json.loads(logMessageIdList)
        if not data:
            return {"statusCode": 500, "body": "Error: Illegal log message"}

        boto3_session = boto3.session.Session()
        ddb = boto3_session.resource("dynamodb")
        table = ddb.Table(table_name)
        response = table.get_item(Key={'SessionId': connection_id})
        if not response:
            return {"statusCode": 500, "body": "Error: Illegal history when find delete message"}

        history = response['Item']['History']
        index = 0
        for item in data:
            print(item)
            item = item - index
            print(item)
            popItem = history.pop(item)
            index = index - 1
            print(f"delete popItem:{popItem}")

        table.update_item(
            Key={'SessionId': connection_id},
            UpdateExpression='SET History = :new_history',
            ExpressionAttributeValues={
                ':new_history': history
            }
        )

        return {"statusCode": 200, "body": "Success"}
        
    except Exception as e:
        print("Error:", e)
        # 这里捕获所有未预料到的异常，并返回500错误
        print("An unexpected error occurred:", str(e))
        return {"statusCode": 500, "body": "Internal Server Error: " + str(e)}











