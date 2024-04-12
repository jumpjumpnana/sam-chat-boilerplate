import os
import boto3
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
from chat import chat

# environment variables
model_id = os.environ.get("ModelId", "anthropic.claude-v2:1")
session_table_name = os.environ["SessionTableName"]
cd_table_name = os.environ["CDTableName"]
ai_prefix = os.environ.get(
    "AI_Prefix",
    # by default (Claude), this is "Assistant"
    "Assistant",
)
prompt_template = os.environ.get(
    "PromptTemplate",
    # by default (Claude)
    "\\n{history}\\n\\nHuman: {input}\\n\\nAssistant:\\n",
).replace("\\n", "\n")

# init dependencies outside of handler
llm = Bedrock(model_id=model_id, streaming=True)
prompt = PromptTemplate.from_template(prompt_template)
boto3_session = boto3.session.Session()


def handler(event, context):
    # call the common chat function in the layer/langchain_common/chat.py
    chat(event, llm, boto3_session, session_table_name,cd_table_name, ai_prefix, prompt)
    return {"statusCode": 200}
