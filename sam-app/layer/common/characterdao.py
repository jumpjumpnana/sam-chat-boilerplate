import boto3
from typing import Optional
from boto3 import Session




# CharacterDefinition对象
class CharacterDefinition:
    def __init__(self, id: str, greeting: Optional[str] = None
        , personality: Optional[str] = None, scenario: Optional[str] = None, example: Optional[str] = None):
        self.id = id
        self.greeting = greeting
        self.personality = personality
        self.scenario = scenario
        self.example = example

    def to_dict(self):
        item_dict = {
            'id': self.id
        }
        if self.greeting:
            item_dict['greeting'] = self.greeting
        if self.personality:
            item_dict['personality'] = self.personality
        if self.scenario:
            item_dict['scenario'] = self.scenario
        if self.example:
            item_dict['example'] = self.example
        return item_dict


# 保存数据到 DynamoDB
def save_character_definition(session: Session,table_name: str,item):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    response = table.put_item(Item=item)
    return response

# 更新数据到 DynamoDB
def update_character_definition(session: Session,table_name: str,id: str, updated_values: dict):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    response = table.update_item(
        Key={'id': id},  # 指定主键 id
        UpdateExpression='SET #n = :val',  # 更新表达式，设置属性名为 #n 的值为 :val
        ExpressionAttributeNames={'#n': 'name'},  # 定义属性名映射
        ExpressionAttributeValues={':val': updated_values['name']}  # 定义属性值映射
    )
    return response
# 删除数据从 DynamoDB
def delete_character_definition(session: Session,table_name: str,id: str):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    response = table.delete_item(
        Key={'id': id}  # 指定要删除的项目的主键 id
    )
    return response

