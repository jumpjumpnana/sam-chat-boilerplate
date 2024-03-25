import os
import boto3
from langchain.llms.openai import OpenAI
from langchain.chains.conversation.prompt import PROMPT
from chat import chat
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate,
    PromptTemplate
)
from langchain_community.chat_models import ChatDeepInfra

# from mistralai.client import MistralClient
# from mistralai.models.chat_completion import ChatMessage

# environment variables
session_table_name = os.environ["SessionTableName"]
api_base = os.environ.get("API_Base")  # default is official API
api_key = os.environ.get(
    "API_Key",
    # for a self-host endpoint, the api_key is needed but can be anything
    "test",
)
model_name = os.environ.get("Model_Name")

# init dependencies outside of handler
# llm = OpenAI(
#     openai_api_base=api_base,
#     openai_api_key=api_key,
#     model_name = model_name,
#     streaming=True,
# )

os.environ['DEEPINFRA_API_TOKEN'] = api_key
llm = ChatDeepInfra(model=model_name,streaming=True)
llm.model_kwargs = {'temperature': 0.7, 'repetition_penalty': 1.2, 'max_new_tokens': 200, 'top_p': 0.9}
print("model:"+model_name)


boto3_session = boto3.session.Session()
ai_prefix = "AI"  # use default
prompt = ChatPromptTemplate  # use default


def handler(event, context):
    # call the common chat function in the layer/langchain_common/chat.py
    chat(event, llm, boto3_session, session_table_name, ai_prefix, prompt)
    return {"statusCode": 200}
