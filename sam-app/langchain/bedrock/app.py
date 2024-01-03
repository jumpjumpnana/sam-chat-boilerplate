import json
from langchain.memory.chat_message_histories import DynamoDBChatMessageHistory
import os
import boto3
from langchain.llms.bedrock import Bedrock
from langchain.chains import ConversationChain
from callback import APIGatewayWebSocketCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# environment variables
model_id = os.environ.get("ModelId", "anthropic.claude-v2:1")
session_table_name = os.environ["SessionTableName"]
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

# init clients outside of handler
llm = Bedrock(model_id=model_id, streaming=True)
prompt = PromptTemplate.from_template(prompt_template)
session = boto3.session.Session()


def handler(event, context):
    print(json.dumps(event))
    connection_id = event["requestContext"]["connectionId"]
    body = json.loads(event["body"])

    # set callback handler
    # so that every time the model generates a response,
    # it is sent to the client
    llm.callbacks = [APIGatewayWebSocketCallbackHandler(session, event)]

    history = DynamoDBChatMessageHistory(
        table_name=session_table_name,
        session_id=connection_id,
        boto3_session=session,
    )
    memory = ConversationBufferMemory(ai_prefix=ai_prefix, chat_memory=history)
    conversation = ConversationChain(llm=llm, memory=memory)
    conversation.prompt = prompt

    conversation.predict(input=body["input"])

    return {
        "statusCode": 200,
    }
