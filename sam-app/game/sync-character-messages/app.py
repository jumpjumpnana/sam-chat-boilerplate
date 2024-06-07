
import os
import boto3
import base64
import json
import requests
from typing import List, Optional
import traceback


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
    get_character_messages,
    update_character_messages,
    get_updated_character_messages
)

cm_table_name = os.environ["CMTableName"]

def handler(event, context):
    # 查询今天的所有数据同步到mysql
    boto3_session = boto3.session.Session()
    character_messages = get_updated_character_messages(boto3_session, cm_table_name)
    if character_messages:
        json_list = []
        for char_message in character_messages:
            print(char_message.to_dict())
            json_list.append(char_message.to_dict())  


        # 将 JSON 列表转换为 JSON 字符串
        characterList = json.dumps(json_list)
        # 定义请求的 URL
        url = 'http://47.251.23.202:8080/ucenter/syncCharacterMessages'

        json_data = {
            'characterList': characterList
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


    return {"statusCode": 200, "body": "Success"}


