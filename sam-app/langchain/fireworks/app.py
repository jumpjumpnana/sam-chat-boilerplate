import os
import boto3
from langchain.chains.conversation.prompt import PROMPT
from chat import chat
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate,
    PromptTemplate
)
from langchain_fireworks import ChatFireworks
# from langchain_community.chat_models import ChatFireworks

# environment variables
session_table_name = os.environ["SessionTableName"]
cd_table_name = os.environ["CDTableName"]
cm_table_name = os.environ["CMTableName"]
um_table_name = os.environ["UMTableName"]
chat_setting_table_name = os.environ["ChatSettingTableName"]
api_base = os.environ.get("API_Base")  # default is official API
api_key = os.environ.get(
    "API_Key",
    # for a self-host endpoint, the api_key is needed but can be anything
    "test",
)
model_name = os.environ.get("Model_Name")


os.environ['FIREWORKS_API_KEY'] = api_key
llm = ChatFireworks(model=model_name,streaming=True)
llm.model_kwargs = {"max_tokens":200,'temperature': 0.7, 'top_p': 0.9}

print("model:"+model_name)


boto3_session = boto3.session.Session()
ai_prefix = "AI"  # use default
prompt = ChatPromptTemplate  # use default


def handler(event, context):
    # call the common chat function in the layer/langchain_common/chat.py
    chat(event, llm, boto3_session, session_table_name,cd_table_name,cm_table_name,um_table_name, ai_prefix, prompt,'ChatFireworks')
    return {"statusCode": 200}


# "model": "accounts/fireworks/models/mixtral-8x7b-instruct", "max_tokens": 4096, "top_p": 1, "top_k": 40, "presence_penalty": 0, "frequency_penalty": 0, "temperature": 0.6, "messages": []