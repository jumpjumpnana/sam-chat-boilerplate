import boto3
from typing import Optional
from boto3 import Session
from botocore.exceptions import ClientError




# UserMessages对象
class UserMessages:
    def __init__(self, uid: str, messages: int = 0, limitMessages: int = 0):
        self.uid = uid
        self.messages = messages
        self.limitMessages = limitMessages

    def to_dict(self):
        item_dict = {
            'uid': self.uid,
            'messages': self.messages,
            'limitMessages': self.limitMessages
        }
       
        return item_dict

    def from_dict(self, item_dict: dict):
        self.uid = item_dict.get('uid')
        self.messages = item_dict.get('messages',0)
        self.limitMessages = item_dict.get('limitMessages',0)


# 保存数据到 DynamoDB
def save_user_messages(session: Session,table_name: str,item):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    response = table.put_item(Item=item)
    return response

# 更新数据到 DynamoDB
def update_user_messages(session: Session,table_name: str,uid: str, name: str,updated_values: dict):
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
def delete_user_messages(session: Session,table_name: str,uid: str):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    response = table.delete_item(
        Key={'uid': uid}  # 指定要删除的项目的主键 uid
    )
    return response

def get_user_messages(session: Session, table_name: str, uid: str) -> Optional[UserMessages]:
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    try:
        response = table.get_item(Key={'uid': uid})
        item = response.get('Item')
        if item:
            char_def = UserMessages(
                uid=item['uid'],
                messages=item.get('messages',0),
                limitMessages=item.get('limitMessages',0)
            )
            return char_def
        else:
            return None
    except ClientError as e:
        print("Error:", e)
        return None

