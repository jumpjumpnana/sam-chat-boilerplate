
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
    get_user_messages,
    update_user_messages,
    update_user_limitMessages
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
        messages = int(body.get('messages', 0))  # 默认为0，避免没有提供时产生错误
        limitMessages = int(body.get('limitMessages', 0))  # 同上
        
        print(f"token: {token}, messages: {messages}, limitMessages: {limitMessages}")

        uid = decode_token(token)
        if uid is None:
            return {"statusCode": 500, "body": "Error: Decoded token is None"}

        boto3_session = boto3.session.Session()

        # 查询userMessages对象，没有则新建
        user_messages = get_user_messages(boto3_session, um_table_name,uid)

        # 根据messages值决定是否执行更新
        if messages != 0:
            response = update_user_messages(boto3_session, um_table_name, uid, messages)
            print("update_user_messages response:", response)

        # 根据limitMessages值决定是否执行更新
        if limitMessages != 0:
            response = update_user_limitMessages(boto3_session, um_table_name, uid, limitMessages)
            print("update_user_limitMessages response:", response)
        
        return {"statusCode": 200, "body": json.dumps(response)}  # 确保响应体也是json格式
        
    except Exception as e:
        # 这里捕获所有未预料到的异常，并返回500错误
        print("An unexpected error occurred:", str(e))
        return {"statusCode": 500, "body": "Internal Server Error: " + str(e)}





