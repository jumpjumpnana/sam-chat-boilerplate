import boto3
from typing import Optional
from boto3 import Session
from botocore.exceptions import ClientError




# UserMessages对象
class ChatSetting:
    def __init__(self, uid: str, temperature: str, repetition_penalty: str,max_new_tokens: str,top_p: str):
        self.uid = uid
        self.temperature = temperature
        self.repetition_penalty = repetition_penalty
        self.max_new_tokens = max_new_tokens
        self.top_p = top_p


    def to_dict(self):
        item_dict = {
            'uid': self.uid,
            'temperature': self.temperature,
            'repetition_penalty': self.repetition_penalty
            'max_new_tokens': self.max_new_tokens
            'top_p': self.top_p
        }
       
        return item_dict

    def from_dict(self, item_dict: dict):
        self.uid = item_dict.get('uid')
        self.temperature = item_dict.get('temperature')
        self.repetition_penalty = item_dict.get('repetition_penalty')
        self.max_new_tokens = item_dict.get('max_new_tokens')
        self.top_p = item_dict.get('top_p')


# 保存数据到 DynamoDB
def save_chat_setting(session: Session,table_name: str,item):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    response = table.put_item(Item=item)
    return response

# 更新数据到 DynamoDB
def update_chat_setting(session: Session,table_name: str,uid: str, name: str,updated_values: dict):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    response = table.update_item(
        Key={'uid': uid},  # 指定主键 uid
        UpdateExpression='SET #n = :val',  # 更新表达式，设置属性名为 #n 的值为 :val
        ExpressionAttributeNames={'#n': name},  # 定义属性名映射
        ExpressionAttributeValues={':val': updated_values[name]}  # 定义属性值映射
    )
    return response
# 删除数据从 DynamoDB
def delete_chat_setting(session: Session,table_name: str,uid: str):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    response = table.delete_item(
        Key={'uid': uid}  # 指定要删除的项目的主键 uid
    )
    return response

def get_chat_setting(session: Session, table_name: str, uid: str) -> Optional[ChatSetting]:
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    try:
        response = table.get_item(Key={'uid': uid})
        item = response.get('Item')
        if item:
            char_def = ChatSetting(
                uid=item['uid'],
                temperature=item.get('temperature'),
                repetition_penalty=item.get('repetition_penalty'),
                max_new_tokens=item.get('max_new_tokens'),
                top_p=item.get('top_p')
            )
            return char_def
        else:
            return None
    except ClientError as e:
        print("Error:", e)
        return None

