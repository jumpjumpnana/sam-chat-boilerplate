import boto3
from typing import Optional
from boto3 import Session
from botocore.exceptions import ClientError
from typing import List, Optional
from boto3.dynamodb.conditions import Key, Attr





# CharacterMessages对象 cid:characterId
class CharacterMessages:
    def __init__(self, cid: str, popular: int = 0, recent: int = 0, trending: int = 0, totalMessages: int = 0,updateFlag: int = 0):
        self.cid = cid
        self.popular = popular
        self.recent = recent
        self.trending = trending
        self.totalMessages = totalMessages
        self.updateFlag = updateFlag


    def to_dict(self):
        item_dict = {
            'cid': self.cid,
            'popular': int(self.popular),
            'recent': int(self.recent),
            'trending': int(self.trending),
            'totalMessages': int(self.totalMessages),
            'updateFlag': self.updateFlag
        }
           
        return item_dict

    def from_dict(self, item_dict: dict):
        self.cid = item_dict.get('cid')
        self.popular = item_dict.get('popular',0)
        self.recent = item_dict.get('recent',0)
        self.trending = item_dict.get('trending',0)
        self.totalMessages = item_dict.get('totalMessages',0)
        self.updateFlag = item_dict.get('updateFlag',0)


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
                popular = item.get('popular',0),
                recent = item.get('recent',0),
                trending = item.get('trending',0),
                totalMessages = item.get('totalMessages',0),
                updateFlag = item.get('updateFlag',0)
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
        # 查询updateFlag的值
        response = table.get_item(Key={'cid': cid}, ProjectionExpression='updateFlag')  # 只查询updateFlag字段以提高效率
        
        # 检查查询结果是否存在且updateFlag是否为1
        if 'Item' in response and response['Item'].get('updateFlag') != 1:
            # updateFlag不是1，执行更新操作
            print("updateFlag不是1，执行更新操作")
            update_expression = "SET popular = popular + :increment, recent = recent + :increment, trending = trending + :increment, totalMessages = totalMessages + :increment, updateFlag = :newFlagValue"
            expression_attribute_values = {":increment": 1, ":newFlagValue": 1}
        else:
            # updateFlag是1，不更新
            print("updateFlag是1，不更新")
            update_expression = "SET popular = popular + :increment, recent = recent + :increment, trending = trending + :increment,totalMessages = totalMessages + :increment"
            expression_attribute_values = {":increment": 1}

        # 执行更新
        update_response = table.update_item(
            Key={'cid': cid},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        return update_response
            
    except ClientError as e:
        print("Error:", e)
        return None

def get_updated_character_messages(session: Session, table_name: str) -> Optional[List[CharacterMessages]]:
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    
    # 使用全局二级索引进行查询
    try:
        response = table.query(
            IndexName='UpdateFlagIndex',  # 假设GSI的名称为'PublicFlagIndex'
            KeyConditionExpression=Key('updateFlag').eq(1),  # 查询publicFlag等于1的记录
        )
        items = response.get('Items', [])
        if items:
            char_defs = [CharacterMessages(cid=item['cid'], 
                popular=item.get('popular', 0),
                recent=item.get('recent', 0),
                trending=item.get('trending', 0),
                totalMessages=item.get('totalMessages', 0)) for item in items]
            return char_defs
        else:
            return []
    except ClientError as e:
        print("Error:", e)
        return None

def batch_update_updated_character_messages(session: Session, table_name: str, char_defs: List[CharacterMessages]) -> None:
    """
    批量更新查询到的CharacterMessages记录，将updateFlag设置为0。
    :param session: AWS Session实例
    :param table_name: DynamoDB表名
    :param char_defs: 需要更新的CharacterMessages对象列表
    """
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    with table.batch_writer() as batch:
        for char_def in char_defs:
            try:
                batch.put_item(
                    Item={
                        'cid': char_def.cid,
                        'popular': char_def.popular,
                        'recent': char_def.recent,
                        'trending': char_def.trending,
                        'totalMessages': char_def.totalMessages,
                        'updateFlag': 0,  # 更新updateFlag为0
                        # 如果有其他字段需要保持原样，可以从char_def中提取并放入Item中
                    }
                )
            except ClientError as e:
                print(f"Error updating item {char_def.cid}: {e}")




