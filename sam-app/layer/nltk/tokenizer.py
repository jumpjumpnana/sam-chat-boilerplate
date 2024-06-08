
import os
import base64
import requests
import time
from datetime import datetime, timedelta

import json
from boto3 import Session
import subprocess
import re

# print("========")
# os.system('df')
# # 列出文件系统信息
# fs_info = subprocess.check_output(['df', '-h']).decode('utf-8')
# print("Filesystem Info:\n", fs_info)

# # 列出 /opt 目录内容
# opt_contents = os.listdir('/opt')
# print("/opt contents:", opt_contents)

# # 列出 /opt/python 目录内容
# if 'python' in opt_contents:
#     python_contents = os.listdir('/opt/python')
#     print("/opt/python contents:", python_contents)

#     # 检查 /opt/python/nltk_data 目录
#     if 'nltk_data' in python_contents:
#         nltk_data_contents = os.listdir('/opt/python/nltk_data')
#         print("/opt/python/nltk_data contents:", nltk_data_contents)
#     else:
#         print("nltk_data directory NOT found in /opt/python")
# else:
#     print("python directory NOT found in /opt")

import nltk
nltk.data.path.append('/opt/python/nltk_data')

from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize



from common import (
    get_date_time,
    decode_base64_to_string,
    decode_token
)


# 截取回复
def get_complete_sentences(text):
    # 使用 sent_tokenize 将文本分成句子
    sentences = sent_tokenize(text)
    
    # 获取所有完整的句子
    complete_text = ' '.join(sentences[:-1])
    last_sentence = sentences[-1]
    
    # 正则表达式来匹配句子的结尾标点符号
    if re.match(r'.*[\.\!\?\"\']$', text.strip()):
        complete_text += ' ' + last_sentence
    
    return complete_text.strip()

# 分词，会去掉空格
def word_tokenize(text):
    return nltk.tokenize.word_tokenize(text)

# 分词获取长度
def get_num_tokens(messages):
    message_str = " ".join([msg.content for msg in messages])
    tokens = word_tokenize(message_str)
    num_tokens = len(tokens)
    # print(f"num_tokens:{num_tokens}")
    return num_tokens
# 分词，不去掉空格   
def tokenize_with_spaces(text):
    # 使用正则表达式进行分词，保留空格
    tokens = re.findall(r'\S+|\s+', text)
    return tokens

# 截取history
def trim_history(history_message,sysMessagesStr,returnStr, max_token_limit):

    num_tokens = get_num_tokens(history_message)
    # 检查是否超过最大令牌限制
    exceeds_limit = num_tokens > max_token_limit
    print(f"exceeds_limit:{exceeds_limit}")
    if num_tokens > max_token_limit:
        pruned_memory = []
        while num_tokens > max_token_limit:
            pruned_memory.append(history_message.pop(0))
            num_tokens = get_num_tokens(history_message)
        return history_message
    return None


