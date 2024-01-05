import os
import boto3
from langchain.llms.openai import OpenAI
from langchain.chains.conversation.prompt import PROMPT
from chat import chat

session_table_name = os.environ["SessionTableName"]
open_ai_api_base = os.environ["OpenAI_API_Base"]

llm = OpenAI(openai_api_base=open_ai_api_base, openai_api_key="test", streaming=True)
boto3_session = boto3.session.Session()
ai_prefix = "AI"  # use default
prompt = PROMPT  # use default


def handler(event, context):
    chat(event, llm, boto3_session, session_table_name, ai_prefix, prompt)
    return {"statusCode": 200}
