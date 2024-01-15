import os
import boto3
from langchain.llms.openai import OpenAI
from langchain.chains.conversation.prompt import PROMPT
from chat import chat

# environment variables
session_table_name = os.environ["SessionTableName"]
open_ai_api_base = os.environ.get("OpenAI_API_Base")  # default is official API
openai_api_key = os.environ.get(
    "OpenAI_API_Key",
    # for a self-host endpoint, the api_key is needed but can be anything
    "test",
)

# init dependencies outside of handler
llm = OpenAI(
    openai_api_base=open_ai_api_base,
    openai_api_key=openai_api_key,
    streaming=True,
)
boto3_session = boto3.session.Session()
ai_prefix = "AI"  # use default
prompt = PROMPT  # use default


def handler(event, context):
    # call the common chat function in the layer/langchain_common/chat.py
    chat(event, llm, boto3_session, session_table_name, ai_prefix, prompt)
    return {"statusCode": 200}
