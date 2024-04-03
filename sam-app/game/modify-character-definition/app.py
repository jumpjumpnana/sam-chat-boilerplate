
import os
import boto3
import base64
import json

from boto3 import Session
from characterdao import (
    CharacterDefinition,
    save_character_definition,
    update_character_definition,
    delete_character_definition
)


session_table_name = os.environ["SessionTableName"]
session = boto3.session.Session()
def handler(event, context):
    bodyJson = event["body"]
    bd = json.dumps(bodyJson)
    body = json.loads(bd)

    print("body:"+str(body))

    # key:characterId_index
    id = body.get("id")
    modify = body.get("modify")
    greeting = body.get("greeting")
    personality = body.get("personality")
    scenario = body.get("scenario")
    example = body.get("example")
    
    try:
        # 保存数据
        if modify == 0:
            cd = CharacterDefinition(id=id, greeting=greeting, personality=personality, scenario=scenario, example=example)
            item = cd.to_dict()
            save_response = save_character_definition(session,session_table_name,item)
            print('Save response:', save_response)
        # 更新数据
        elif modify == 1:
            if greeting is not None:
                updated_values = {'greeting': greeting}  # 要更新的值
                update_response = update_character_definition(session,session_table_name,id,'greeting', updated_values)
                print('Update greeting response:', update_response)
            if personality is not None:
                updated_values = {'personality': personality}  # 要更新的值
                update_response = update_character_definition(session,session_table_name,id,'personality', updated_values)
                print('Update personality response:', update_response)
            if scenario is not None:
                updated_values = {'scenario': scenario}  # 要更新的值
                update_response = update_character_definition(session,session_table_name,id,'scenario', updated_values)
                print('Update scenario response:', update_response)
            if example is not None:
                updated_values = {'example': example}  # 要更新的值
                update_response = update_character_definition(session,session_table_name,id,'example', updated_values)
                print('Update example response:', update_response)
        # 删除数据
        elif modify == 2:
            delete_response = delete_character_definition(session,session_table_name,id)
            print('Delete response:', delete_response)
        else:
            return {"statusCode": 200, "body": "Invalid modify value. Must be 0 (save) or 1 (update) or 2 (delete)."}

    except Exception as e:
        print("Error:", e)
        error_message = "Exception: " + str(e)
        return {"statusCode": 200, "body": error_message}

    return {"statusCode": 200, "body": "invalid route"}


