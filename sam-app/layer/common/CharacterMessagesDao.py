import boto3
from typing import Optional
from boto3 import Session
from botocore.exceptions import ClientError
from typing import List, Optional
from boto3.dynamodb.conditions import Key, Attr

from common import (
    get_date_time,
    decode_base64_to_string
)


# CharacterMessages对象 cid:characterId_dateTime时间戳,updateFlag:dateTime时间戳
class CharacterMessages:
    def __init__(self, cid: str, totalMessages: int,updateFlag: str):
        self.cid = cid
        self.totalMessages = totalMessages
        self.updateFlag = updateFlag


    def to_dict(self):
        item_dict = {
            'cid': self.cid,
            'totalMessages': int(self.totalMessages),
            'updateFlag': self.updateFlag
        }
           
        return item_dict

    def from_dict(self, item_dict: dict):
        self.cid = item_dict.get('cid')
        self.totalMessages = item_dict.get('totalMessages',0)
        self.updateFlag = item_dict.get('updateFlag')


# 保存数据到 DynamoDB
def save_character_messages(session: Session,table_name: str,item):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    response = table.put_item(Item=item)
    return response


def get_character_messages(session: Session, table_name: str, cid: str) -> Optional[CharacterMessages]:
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    try:
        response = table.get_item(Key={'cid': cid})
        item = response.get('Item')
        if item:
            char_def = CharacterMessages(
                cid=item['cid'],
                totalMessages = item.get('totalMessages',0),
                updateFlag = item.get('updateFlag')
            )
            return char_def
        else:
            return None
    except ClientError as e:
        print("Error:", e)
        return None


def update_character_messages(session: Session, table_name: str, cid: str):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    
    try:
        dateTime = get_date_time()
        cmId = f"{cid}_{dateTime}"
        # 查询updateFlag的值
        response = table.get_item(Key={'cid': cmId}, ProjectionExpression='updateFlag')  # 只查询updateFlag字段以提高效率
        
        # 检查查询结果是否存在
        if 'Item' in response:
            update_expression = "SET totalMessages = totalMessages + :increment"
            expression_attribute_values = {":increment": 1}

            # 执行更新
            update_response = table.update_item(
                Key={'cid': cmId},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            return update_response
        else:
            # 如果没有找到Item，则新建
            print("未找到记录，创建新记录")
            new_record = {
                'cid': cmId,
                'totalMessages': 1,  # 新记录默认totalMessages为1
                'updateFlag': dateTime  # 初始化updateFlag
            }
            new_response = table.put_item(Item=new_record)
            return new_response
            
        
    except ClientError as e:
        print("Error:", e)
        return None

def get_updated_character_messages(session: Session, table_name: str) -> Optional[List[CharacterMessages]]:
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    
    # 使用全局二级索引进行查询
    try:
        dateTime = get_date_time()
        updateFlag = dateTime
        response = table.query(
            IndexName='UpdateFlagIndex',  # 假设GSI的名称为'UpdateFlagIndex'
            KeyConditionExpression=Key('updateFlag').eq(updateFlag),  
        )
        items = response.get('Items', [])
        if items:
            char_defs = [CharacterMessages(cid=item['cid'], 
                totalMessages=item.get('totalMessages', 0),
                updateFlag=item.get('updateFlag')) for item in items]
            return char_defs
        else:
            return []
    except ClientError as e:
        print("Error:", e)
        return None

# def batch_update_updated_character_messages(session: Session, table_name: str, char_defs: List[CharacterMessages]) -> None:
#     """
#     批量更新查询到的CharacterMessages记录，将updateFlag设置为0。
#     :param session: AWS Session实例
#     :param table_name: DynamoDB表名
#     :param char_defs: 需要更新的CharacterMessages对象列表
#     """
#     ddb = session.resource("dynamodb")
#     table = ddb.Table(table_name)
#     with table.batch_writer() as batch:
#         for char_def in char_defs:
#             try:
#                 date_part = char_def.updateFlag.split('_')[0]  # 提取日期时间戳部分
#                 new_update_flag = f"{date_part}_0"  
#                 batch.put_item(
#                     Item={
#                         'cid': char_def.cid,
#                         'totalMessages': char_def.totalMessages,
#                         'updateFlag': new_update_flag,  # 更新updateFlag为0
#                         # 如果有其他字段需要保持原样，可以从char_def中提取并放入Item中
#                     }
#                 )
#             except ClientError as e:
#                 print(f"Error updating item {char_def.cid}: {e}")

