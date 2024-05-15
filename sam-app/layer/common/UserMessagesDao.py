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
            'messages': int(self.messages),
            'limitMessages': int(self.limitMessages)
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

def get_user_messages(session: Session, table_name: str, uid: str) -> Optional[UserMessages]:
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    try:
        response = table.get_item(Key={'uid': uid})
        item = response.get('Item')
        if item:
            char_def = UserMessages(
                uid=item['uid'],
                messages = item.get('messages',0),
                limitMessages = item.get('limitMessages',0)
            )
            return char_def
        else:
            # 如果没有找到记录，则创建新记录
            print(f"未找到UserMessages{uid}的记录，创建新记录")
            # 设置初始值
            initial_messages = 0
            initial_limit = 0  
            
            # 构造新记录
            new_record = {
                'uid': uid,
                'messages': initial_messages,
                'limitMessages': initial_limit
            }
            
            # 插入新记录
            table.put_item(Item=new_record)
            
            # 返回新创建的UserMessages实例
            return UserMessages(
                uid=uid,
                messages=initial_messages,
                limitMessages=initial_limit
            )
    except ClientError as e:
        print("Error:", e)
        return None


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



def update_user_messages(session: Session, table_name: str, uid: str,increment_value: int):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    
    # add
    try:
        response = table.update_item(
            Key={'uid': uid},
            UpdateExpression="SET messages = messages + :inc",
            ExpressionAttributeValues={
                ":inc": increment_value
            }
        )

        return response

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print("更新失败，因为messages字段将会小于0")
        else:
            print("Error:", e)
        return None


def update_user_limitMessages(session: Session, table_name: str, uid: str,increment_value: int):
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    
    # add
    try:
        response = table.update_item(
            Key={'uid': uid},
            UpdateExpression="SET limitMessages = limitMessages + :inc",
            ExpressionAttributeValues={
                ":inc": increment_value
            }
        )

        return response

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print("更新失败，因为limitMessages字段将会小于0")
        else:
            print("Error:", e)
        return None


def deduct_user_messages(session: Session, table_name: str, uid: str, deduct_amount: int) -> bool:
    """
    扣除用户消息数，先扣除limitMessages，不足时再扣除messages，保证不会扣成负数。

    参数:
    deduct_amount -- 每次需要扣除的消息数量

    返回:
    如果扣除成功且最终剩余消息数非负，则返回True，否则返回False。
    """
    ddb = session.resource("dynamodb")
    table = ddb.Table(table_name)
    total_deducted = 0  # 记录总共已扣除的消息数

    # 先尝试从limitMessages中扣除
    while deduct_amount > 0:
        try:
            # 获取当前的limitMessages值
            response = table.get_item(Key={'uid': uid})
            current_messages = response.get('Item', {}).get('messages', 0)
            current_limit_messages = response.get('Item', {}).get('limitMessages', 0)
            
            # 检查总和是否足够扣除
            total_available = current_messages + current_limit_messages
            if total_available < deduct_amount:
                print("消息总数不足以完成扣除")
                return False            
            # 计算本次能扣除的最大值，防止limitMessages变负
            deduct_this_round = min(deduct_amount, current_limit_messages)
            
            # 尝试更新limitMessages
            if deduct_this_round > 0:
                response_update = table.update_item(
                    Key={'uid': uid},
                    UpdateExpression="SET limitMessages = limitMessages - :deduct_this_round",
                    ConditionExpression="limitMessages >= :deduct_this_round",
                    ExpressionAttributeValues={
                        ":deduct_this_round": deduct_this_round
                    },
                    ReturnValues="UPDATED_NEW"
                )
                
                # 更新成功则累加已扣除数量
                total_deducted += deduct_this_round
                deduct_amount -= deduct_this_round
                
        except ClientError as e:
            print("Error during limitMessages deduction:", e)
            return False

    # 如果还有剩余需要扣除，尝试从messages中扣除
    if deduct_amount > 0:
        try:
            # 获取当前的messages值
            response = table.get_item(Key={'uid': uid})
            current_messages = response.get('Item', {}).get('messages', 0)
            
            # 计算本次能扣除的最大值，防止messages变负
            deduct_this_round = min(deduct_amount, current_messages)
            
            # 尝试更新messages
            if deduct_this_round > 0:
                response_update = table.update_item(
                    Key={'uid': uid},
                    UpdateExpression="SET messages = messages - :deduct_this_round",
                    ConditionExpression="messages >= :deduct_this_round",
                    ExpressionAttributeValues={
                        ":deduct_this_round": deduct_this_round
                    },
                    ReturnValues="UPDATED_NEW"
                )
                
                # 更新成功则累加已扣除数量
                total_deducted += deduct_this_round
                deduct_amount -= deduct_this_round
                
        except ClientError as e:
            print("Error during messages deduction:", e)
            return False

    # 如果最终扣除量等于初始扣除需求，说明扣除成功且没有变为负数
    return total_deducted == deduct_amount

# def update_user_messages(session: Session, table_name: str, uid: str, name: str, updated_values: dict):
#     ddb = session.resource("dynamodb")
#     table = ddb.Table(table_name)

#     response = table.get_item(Key={'uid': uid})
#     if 'version' not in response.get('Item', {}):
#         table.update_item(
#             Key={'uid': uid},
#             UpdateExpression='SET #v = :default_version',
#             ExpressionAttributeNames={'#v': 'version'},
#             ExpressionAttributeValues={':default_version': 0}
#         )
#     current_version = int(response.get('Item', {}).get('version', 0))
#     try:
#         response = table.update_item(
#             Key={'uid': uid},
#             UpdateExpression='SET #n = :val, #v = #v + :incr',  
#             ExpressionAttributeNames={'#n': name, '#v': 'version'},  
#             ExpressionAttributeValues={':val': updated_values[name], ':incr': 1, ':current_version': current_version},  # 定义属性值映射，版本号+1
#             ConditionExpression='#v = :current_version', 
#         )
#         return response
#     except ddb.meta.client.exceptions.ConditionalCheckFailedException:
#         # 版本号不一致
#         return {'error': 'Version mismatch, update failed.'}

