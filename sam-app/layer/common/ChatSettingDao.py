import boto3
from typing import Optional
from boto3 import Session
from botocore.exceptions import ClientError

from decimal import Decimal

# UserMessages对象
class ChatSetting:
    def __init__(self, uid: str, temperature: float, repetition_penalty: float,
        top_p: float,top_k: int,max_tokens: int,memory_size: int,presence_penalty: int,reply_style: int):
        self.uid = uid
        self.temperature = temperature
        self.repetition_penalty = repetition_penalty
        self.top_p = top_p
        self.top_k = top_k
        self.max_tokens = max_tokens
        self.memory_size = memory_size
        self.presence_penalty = presence_penalty
        self.reply_style = reply_style
        

    def to_dict(self):
        item_dict = {
            'uid': self.uid,
            'temperature': Decimal(str(self.temperature)),  # 转换为Decimal类型
            'repetition_penalty': Decimal(str(self.repetition_penalty)),  
            'top_p': Decimal(str(self.top_p)),  
            'top_k': int(self.top_k),
            'max_tokens': int(self.max_tokens),
            'memory_size': int(self.memory_size),
            'presence_penalty': int(self.presence_penalty),
            'reply_style': int(self.reply_style)
        }
       
        return item_dict

    def from_dict(self, item_dict: dict):
        self.uid = item_dict.get('uid')
        self.temperature = item_dict.get('temperature')
        self.repetition_penalty = item_dict.get('repetition_penalty')
        self.top_p = item_dict.get('top_p')
        self.top_k = item_dict.get('top_k')
        self.max_tokens = item_dict.get('max_tokens')
        self.memory_size = item_dict.get('memory_size')
        self.presence_penalty = item_dict.get('presence_penalty')
        self.reply_style = item_dict.get('reply_style')
       


# 保存数据到 DynamoDB
def save_chat_setting(session: Session,table_name: str,item):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    response = table.put_item(Item=item)
    return response

# 更新数据到 DynamoDB
def update_chat_setting(session: Session,table_name: str,uid: str,updated_values: dict):
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
        Key={'uid': uid},
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values
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
                top_p=item.get('top_p'),
                top_k=item.get('top_k'),
                max_tokens=item.get('max_tokens'),
                memory_size=item.get('memory_size'),
                presence_penalty=item.get('presence_penalty'),
                reply_style=item.get('reply_style')
                
            )
            return char_def
        else:
            return None
    except ClientError as e:
        print("Error:", e)
        return None

