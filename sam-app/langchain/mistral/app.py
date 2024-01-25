import os
import boto3
from langchain.llms.openai import OpenAI
from langchain.chains.conversation.prompt import PROMPT
from chat import chat

# from mistralai.client import MistralClient
# from mistralai.models.chat_completion import ChatMessage

# environment variables
session_table_name = os.environ["SessionTableName"]
mistral_api_base = os.environ.get("Mistral_API_Base")  # default is official API
mistral_api_key = os.environ.get(
    "Mistral_API_Key",
    # for a self-host endpoint, the api_key is needed but can be anything
    "test",
)
mistral_model_name = os.environ.get("Mistral_Model_Name")

# init dependencies outside of handler
llm = OpenAI(
    openai_api_base=mistral_api_base,
    openai_api_key=mistral_api_key,
    model_name = mistral_model_name,
    streaming=True,
)
boto3_session = boto3.session.Session()
ai_prefix = "AI"  # use default
prompt = PROMPT  # use default


def handler(event, context):
    # call the common chat function in the layer/langchain_common/chat.py
    chat(event, llm, boto3_session, session_table_name, ai_prefix, prompt)
    return {"statusCode": 200}
