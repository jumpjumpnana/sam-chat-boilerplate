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


def has_sufficient_messages(session: Session, table_name: str, uid: str, deduct_amount: int) -> bool:
    """
    判断用户是否有足够的消息数可以扣除，先检查limitMessages，再检查messages。
    
    参数:
    deduct_amount -- 每次需要扣除的消息数量
    
    返回:
    如果扣除后剩余消息数非负，则返回True，否则返回False。
    """
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    try:
        response = table.get_item(Key={'uid': uid})
        item = response.get('Item')
        if item:
            if (item.get('limitMessages', 0) + item.get('messages', 0)) >= deduct_amount:
                return True
    except Exception as e:
        print(f"Error fetching data from DynamoDB: {e}")
    
    return False


def update_user_messages(session: Session, table_name: str, uid: str, name: str, updated_values: dict):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)

    response = table.get_item(Key={'uid': uid})
    if 'version' not in response.get('Item', {}):
        table.update_item(
            Key={'uid': uid},
            UpdateExpression='SET #v = :default_version',
            ExpressionAttributeNames={'#v': 'version'},
            ExpressionAttributeValues={':default_version': 0}
        )
    current_version = int(response.get('Item', {}).get('version', 0))
    try:
        response = table.update_item(
            Key={'uid': uid},
            UpdateExpression='SET #n = :val, #v = #v + :incr',  
            ExpressionAttributeNames={'#n': name, '#v': 'version'},  
            ExpressionAttributeValues={':val': updated_values[name], ':incr': 1, ':current_version': current_version},  # 定义属性值映射，版本号+1
            ConditionExpression='#v = :current_version', 
        )
        return response
    except ddb.meta.client.exceptions.ConditionalCheckFailedException:
        # 版本号不一致
        return {'error': 'Version mismatch, update failed.'}

