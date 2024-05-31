
import os
import boto3
import base64
import json
import requests
from typing import List, Optional
import traceback
from langchain.memory import DynamoDBChatMessageHistory


from boto3 import Session

from common import (
    get_date_time,
    decode_base64_to_string,
    decode_token
)

from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    PromptTemplate
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
        contentBase = str(body.get('contentBase'))
        uid = decode_token(token)

        if uid is None:
            return {"statusCode": 500, "body": "Error: Decoded token is None"}

        content = decode_base64_to_string(contentBase)
        data = json.loads(content)
        print("data:"+str(data))
        
        if not data:
            return {"statusCode": 500, "body": "Error: Illegal chat saved"}

        # 保存到history
        boto3_session = boto3.session.Session()
        history = DynamoDBChatMessageHistory(
            table_name=table_name,
            session_id=connection_id
        )
        for item in data:
            print(f"message: {item['content']}")
            if item['isUser'] == 0:
                history.add_ai_message(item['content'])
            elif item['isUser'] == 1:
                history.add_user_message(item['content'])

        return {"statusCode": 200, "body": "Success"}
        
    except Exception as e:
        print("Error:", e)
        # 这里捕获所有未预料到的异常，并返回500错误
        print("An unexpected error occurred:", str(e))
        return {"statusCode": 500, "body": "Internal Server Error: " + str(e)}


