
import os
import boto3
import base64
import json
import requests

from boto3 import Session
from characterdao import (
    CharacterDefinition,
    save_character_definition,
    update_character_definition,
    delete_character_definition
)


from common import (
    get_date_time,
    decode_base64_to_string,
    decode_token
)


session_table_name = os.environ["SessionTableName"]
session = boto3.session.Session()


def handler(event, context):
    bodyStr = event["body"]
    bodyJson = decode_base64_to_string(bodyStr)
    body = json.loads(bodyJson)
    print("body:"+str(body))

    # key:characterId_index
    id = body.get("id")
    modify = body.get("modify")
    greeting = body.get("greeting")
    personality = body.get("personality")
    scenario = body.get("scenario")
    example = body.get("example")
    cname = body.get("cname")
    gender = body.get("gender")
    
    try:
        # 保存数据
        if modify == 0:
            cd = CharacterDefinition(id=id, greeting=greeting, personality=personality, 
                scenario=scenario, example=example ,cname=cname,gender=gender)
            item = cd.to_dict()
            save_response = save_character_definition(session,session_table_name,item)
            print('Save response:', save_response)
        # 更新数据
        elif modify == 1:
            updated_values = {
                'greeting': greeting,
                'personality': personality,
                'scenario': scenario,
                'example': example,
                'cname': cname,
                'gender': gender

            }
            update_character_definition(session,session_table_name,id, updated_values)
        # 删除数据
        elif modify == 2:
            delete_response = delete_character_definition(session,session_table_name,id)
            print('Delete response:', delete_response)
        else:
            return {"statusCode": 500, "body": "Invalid modify value. Must be 0 (save) or 1 (update) or 2 (delete)."}
            
        return {"statusCode": 200, "body": "Success"}

    except Exception as e:
        print("Error:", e)
        error_message = "Exception: " + str(e)
        return {"statusCode": 500, "body": error_message}

    


