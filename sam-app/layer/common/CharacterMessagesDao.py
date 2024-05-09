import boto3
from typing import Optional
from boto3 import Session
from botocore.exceptions import ClientError
from typing import List, Optional





# CharacterMessages对象 cid:characterId
class CharacterMessages:
    def __init__(self, cid: str, popular: int = 0, recent: int = 0, trending: int = 0, totalMessages: int = 0):
        self.cid = cid
        self.popular = popular
        self.recent = recent
        self.trending = trending
        self.totalMessages = totalMessages


    def to_dict(self):
        item_dict = {
            'cid': self.cid,
            'popular': self.popular,
            'recent': self.recent,
            'trending': self.trending,
            'totalMessages': self.totalMessages
        }
           
        return item_dict

    def from_dict(self, item_dict: dict):
        self.cid = item_dict.get('cid')
        self.popular = item_dict.get('popular',0)
        self.recent = item_dict.get('recent',0)
        self.trending = item_dict.get('trending',0)
        self.totalMessages = item_dict.get('totalMessages',0)


# 保存数据到 DynamoDB
def save_character_messages(session: Session,table_name: str,item):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    response = table.put_item(Item=item)
    return response

# 更新数据到 DynamoDB
def update_character_messages(session: Session,table_name: str,cid: str, name: str,updated_values: dict):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    response = table.update_item(
        Key={'cid': cid},  # 指定主键 cid
        UpdateExpression='SET #n = :val',  # 更新表达式，设置属性名为 #n 的值为 :val
        ExpressionAttributeNames={'#n': name},  # 定义属性名映射
        ExpressionAttributeValues={':val': updated_values[name]}  # 定义属性值映射
    )
    return response
# 删除数据从 DynamoDB
def delete_character_messages(session: Session,table_name: str,cid: str):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    response = table.delete_item(
        Key={'cid': cid}  # 指定要删除的项目的主键 cid
    )
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
                totalMessages = item.get('totalMessages',0)
            )
            return char_def
        else:
            return None
    except ClientError as e:
        print("Error:", e)
        return None


def update_character_messages(session: Session, table_name: str, cid: str, updated_fields: dict):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    
    update_expression_parts = ["SET"]
    for index, field in enumerate(updated_fields):
        # 如果不是第一个元素，则在当前字段前添加逗号和空格
        if index > 0:
            update_expression_parts.append(", ")
        update_expression_parts.append(f"{field} = {field} + :increment")

    # 使用 join 直接构造完整的 UpdateExpression
    update_expression = " ".join(update_expression_parts)

    expression_attribute_values = {":increment": 1}
    
    try:
        # 执行更新操作
        response = table.update_item(
            Key={'cid': cid},  # 指定主键 cid
            UpdateExpression=update_expression,  # 更新表达式，使用 SET 操作符
            ExpressionAttributeValues=expression_attribute_values  # 定义属性值映射
        )
        return response
        
    except ClientError as e:
        print("Error:", e)
        return None

def get_all_character_messages(session: Session, table_name: str) -> Optional[List[CharacterMessages]]:
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    try:
        response = table.scan()
        items = response.get('Items', [])
        if items:
            char_defs = []
            for item in items:
                char_def = CharacterMessages(
                    cid=item['cid'],
                    popular=item.get('popular', 0),
                    recent=item.get('recent', 0),
                    trending=item.get('trending', 0),
                    totalMessages=item.get('totalMessages', 0)
                )
                char_defs.append(char_def)
            return char_defs
        else:
            return None
    except ClientError as e:
        print("Error:", e)
        return None


