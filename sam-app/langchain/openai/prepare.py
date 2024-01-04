import os
import boto3
from langchain.llms.openai import OpenAI
from langchain.chains.conversation.prompt import PROMPT

session_table_name = os.environ["SessionTableName"]
open_ai_api_base = os.environ["OpenAI_API_Base"]

llm = OpenAI(openai_api_base=open_ai_api_base, openai_api_key="test", streaming=True)
session = boto3.session.Session()
ai_prefix = "AI"  # use default
prompt = PROMPT
