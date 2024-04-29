
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

def decode_base64_to_string(encoded_string):
    # 将编码后的字符串转换为字节
    bytes_to_decode = encoded_string.encode('utf-8')

    # 对字节进行Base64解码
    decoded_bytes = base64.b64decode(bytes_to_decode)

    # 将解码后的字节转换回字符串
    decoded_string = decoded_bytes.decode('utf-8')

    return decoded_string


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
            if cname is not None:
                updated_values = {'cname': cname}  # 要更新的值
                update_response = update_character_definition(session,session_table_name,id,'cname', updated_values)
                print('Update cname response:', update_response)
            if gender is not None:
                updated_values = {'gender': gender}  # 要更新的值
                update_response = update_character_definition(session,session_table_name,id,'gender', updated_values)
                print('Update gender response:', update_response)
        # 删除数据
        elif modify == 2:
            delete_response = delete_character_definition(session,session_table_name,id)
            print('Delete response:', delete_response)
        else:
            return {"statusCode": 500, "body": "Invalid modify value. Must be 0 (save) or 1 (update) or 2 (delete)."}

    except Exception as e:
        print("Error:", e)
        error_message = "Exception: " + str(e)
        return {"statusCode": 500, "body": error_message}

    return {"statusCode": 200, "body": "Success"}


