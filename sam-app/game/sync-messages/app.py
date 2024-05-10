
import os
import boto3
import base64
import json
import requests
from typing import List, Optional


from boto3 import Session
from characterdao import (
    CharacterDefinition,
    save_character_definition,
    update_character_definition,
    delete_character_definition
)
from CharacterMessagesDao import (
    CharacterMessages,
    save_character_messages,
    update_character_messages,
    delete_character_messages,
    get_character_messages,
    update_character_messages,
    get_update_character_messages
)



def handler(event, context):
   
    try:
        boto3_session = boto3.session.Session()
        character_messages = get_update_character_messages(boto3_session, "CharacterMessages")
        if character_messages:
            json_list = []
            for char_message in character_messages:
                json_list.append(char_message.to_dict())  # 假设 CharacterMessages 类有一个 to_dict 方法

            # 将 JSON 列表转换为 JSON 字符串
            characterList = json.dumps(json_list)
            # 定义请求的 URL
            url = 'http://47.251.23.202:8080/ucenter/syncCharacterMessages'

            json_data = {
                'characterList': characterList,
                'test': '111'
            }
            # 发送 GET 请求
            response = requests.post(url,json=json_data)

            # 检查响应状态码
            if response.status_code == 200:
                # 打印响应内容
                print(response.text)
            else:
                # 打印错误信息
                print('Error:', response.status_code)

    except Exception as e:
        print("Error:", e)
        error_message = "Exception: " + str(e)
        return {"statusCode": 500, "body": error_message}

    return {"statusCode": 200, "body": "Success"}


