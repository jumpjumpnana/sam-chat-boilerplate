import boto3
from typing import Optional
from boto3 import Session
from botocore.exceptions import ClientError





# CharacterDefinition对象 id:characterId
class CharacterDefinition:
    def __init__(self, id: str, greeting: Optional[str] = None
        , personality: Optional[str] = None, scenario: Optional[str] = None, example: Optional[str] = None
        , cname: Optional[str] = None, gender: Optional[str] = None):
        self.id = id
        self.greeting = greeting
        self.personality = personality
        self.scenario = scenario
        self.example = example
        self.cname = cname
        self.gender = gender


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
        if self.cname:
            item_dict['cname'] = self.cname
        if self.gender:
            item_dict['gender'] = self.gender
        return item_dict

    def from_dict(self, item_dict: dict):
        self.id = item_dict.get('id')
        self.greeting = item_dict.get('greeting')
        self.personality = item_dict.get('personality')
        self.scenario = item_dict.get('scenario')
        self.example = item_dict.get('example')
        self.cname = item_dict.get('cname')
        self.gender = item_dict.get('gender')


# 保存数据到 DynamoDB
def save_character_definition(session: Session,table_name: str,item):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    response = table.put_item(Item=item)
    return response

# 更新数据到 DynamoDB
def update_character_definition(session: Session,table_name: str,id: str,updated_values: dict):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)

    # 过滤掉值为空的项
    filtered_updated_values = {k: v for k, v in updated_values.items() if v is not None}
    # 如果过滤后没有任何字段需要更新，直接返回不处理这种情况
    if not filtered_updated_values:
        print("No valid fields to update.")
        return None  

    # 构建更新表达式，设置多个属性
    update_expression_parts = ["SET"]  # 初始化SET部分
    expression_attribute_names = {}  # 初始化属性名映射
    expression_attribute_values = {}  # 初始化属性值映射
    
    for key in filtered_updated_values.keys():
        # 为每个字段添加到更新表达式、属性名映射和属性值映射
        update_expression_parts.append(f"#{key} = :{key},")  # 使用#{key}动态引用属性名
        expression_attribute_names[f"#{key}"] = key  # 映射属性名
        expression_attribute_values[f":{key}"] = filtered_updated_values[key]  # 映射属性值

    # 确保正确去除最后一个逗号
    if update_expression_parts[-1].endswith(","):
        update_expression_parts[-1] = update_expression_parts[-1][:-1]

    # 组合更新表达式
    update_expression = ' '.join(update_expression_parts)
        
    # 执行更新操作
    response = table.update_item(
        Key={'id': id},
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values
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

def get_character_definition(session: Session, table_name: str, id: str) -> Optional[CharacterDefinition]:
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    try:
        response = table.get_item(Key={'id': id})
        item = response.get('Item')
        if item:
            char_def = CharacterDefinition(
                id=item['id'],
                greeting=item.get('greeting'),
                personality=item.get('personality'),
                scenario=item.get('scenario'),
                example=item.get('example'),
                cname=item.get('cname'),
                gender=item.get('gender')
            )
            return char_def
        else:
            return None
    except ClientError as e:
        print("Error:", e)
        return None

