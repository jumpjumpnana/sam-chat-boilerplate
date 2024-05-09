import os
import boto3
from langchain_community.chat_models import ChatAnyscale
# from langchain_community.chat_models import ChatOpenAI
# from langchain_community.llms import AnyscaleEmbeddings


from chat import chat
from langchain.prompts import (
    ChatPromptTemplate
)

# environment variables
session_table_name = os.environ["SessionTableName"]
cd_table_name = os.environ["CDTableName"]
cm_table_name = os.environ["CMTableName"]
um_table_name = os.environ["UMTableName"]
chat_setting_table_name = os.environ["ChatSettingTableName"]
open_ai_api_base = os.environ.get("OpenAI_API_Base")  # default is official API
openai_api_key = os.environ.get(
    "OpenAI_API_Key",
    # for a self-host endpoint, the api_key is needed but can be anything
    "test",
)
openai_organization = os.environ.get("OpenAI_Organization")
model_name = os.environ.get("Model_Name")

# init dependencies outside of handler
llm = ChatAnyscale(
    anyscale_api_base=open_ai_api_base,
    anyscale_api_key=openai_api_key,
    model_name=model_name,
    streaming=True
    # temperature=0.7,
    # max_tokens=200
)

boto3_session = boto3.session.Session()
ai_prefix = "AI"  # use default
prompt = ChatPromptTemplate  


def handler(event, context):
    # call the common chat function in the layer/langchain_common/chat.py
    chat(event, llm, boto3_session, session_table_name,cd_table_name,cm_table_name,um_table_name, ai_prefix, prompt)
    return {"statusCode": 200}