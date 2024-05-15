
import os
import base64
import requests
import time
from datetime import datetime, timedelta

import json
from boto3 import Session


from langchain.schema import messages_to_dict




def get_date_time():
    # 获取当前时间的datetime对象
    now = datetime.now()

    # 设置时间为当天的00:00:00
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # 转换为Unix时间戳（整数形式）
    unix_today_start = int(today_start.timestamp())

    return str(unix_today_start)



def decode_base64_to_string(encoded_string):
    # 将编码后的字符串转换为字节
    bytes_to_decode = encoded_string.encode('utf-8')

    # 对字节进行Base64解码
    decoded_bytes = base64.b64decode(bytes_to_decode)

    # 将解码后的字节转换回字符串
    decoded_string = decoded_bytes.decode('utf-8')

    return decoded_string



def decode_token(token):
    try:
        if token is None or token == "":
            print("Decoded token: token is null")
            return None
        # 对编码的字符串进行解码
        decoded_bytes = base64.b64decode(token)
        
        # 从字节数据中构建原始字符串
        original_string = decoded_bytes.decode('utf-8')
        
        print("Decoded token:", original_string)

        strings = original_string.split("_")
        uid = strings[0]
        return str(uid)
    except ValueError:
        print("Error converting uid to integer:", ValueError)
        return None






