
import os
import boto3
import base64
import json
import requests

from boto3 import Session
from ChatSettingDao import (
    ChatSetting,
    get_chat_setting,
    save_chat_setting,
    update_chat_setting,
    delete_chat_setting
)

from common import (
    get_date_time,
    decode_base64_to_string,
    decode_token
)


table_name = os.environ["TableName"]
session = boto3.session.Session()


def handler(event, context):
    bodyStr = event["body"]
    bodyJson = decode_base64_to_string(bodyStr)
    body = json.loads(bodyJson)
    print("body:"+str(body))

    # key:uid
    token = str(body.get('token'))
    modify = int(body.get("modify"))
    temperature = float(body.get("temperature"))
    repetition_penalty = float(body.get("repetition_penalty"))
    top_p = float(body.get("top_p"))
    top_k = int(body.get("top_k"))
    max_tokens = int(body.get("max_tokens"))
    memory_size = int(body.get("memory_size"))
    presence_penalty = int(body.get("presence_penalty"))
    reply_style = int(body.get("reply_style"))

    # print(f"token: {token}, modify: {modify}, temperature: {temperature}, repetition_penalty: {repetition_penalty}, top_p: {top_p}")
    # print(f"top_k: {top_k}, max_tokens: {max_tokens}, memory_size: {memory_size}, presence_penalty: {presence_penalty}, reply_style: {reply_style}")

    uid = decode_token(token)
    if not uid:
        return {"statusCode": 500, "body": "Error: Decoded token is None"}

    try:
        # 新增数据
        if modify == 0:
            cs = ChatSetting(uid=uid, temperature=temperature, repetition_penalty=repetition_penalty, 
                top_p=top_p, top_k=top_k ,max_tokens=max_tokens,memory_size=memory_size,
                presence_penalty=presence_penalty,reply_style=reply_style)
            item = cs.to_dict()
            save_response = save_chat_setting(session,table_name,item)
            print('Save response:', save_response)
        # 更新数据
        elif modify == 1:
            updated_values = {
                'temperature': temperature,
                'repetition_penalty': repetition_penalty,
                'top_p': top_p,
                'top_k': top_k,
                'max_tokens': max_tokens,
                'memory_size': memory_size,
                'presence_penalty': presence_penalty,
                'reply_style': reply_style

            }
            update_chat_setting(session,table_name,uid, updated_values)
        # 删除数据
        elif modify == 2:
            delete_response = delete_chat_setting(session,table_name,uid)
            print('Delete response:', delete_response)
        else:
            return {"statusCode": 500, "body": "Invalid modify value. Must be 0 (save) or 1 (update) or 2 (delete)."}
            
        return {"statusCode": 200, "body": "Success"}

    except Exception as e:
        print("Error:", e)
        error_message = "Exception: " + str(e)
        return {"statusCode": 500, "body": error_message}

    


