import json
from langchain.memory.chat_message_histories import DynamoDBChatMessageHistory
import os
import boto3
from langchain.llms.openai import OpenAI
from langchain.chains import ConversationChain
from callback import APIGatewayWebSocketCallbackHandler
from langchain.memory import ConversationBufferMemory

session_table_name = os.environ["SessionTableName"]
open_ai_api_base = os.environ["OpenAI_API_Base"]

llm = OpenAI(openai_api_base=open_ai_api_base, openai_api_key="test", streaming=True)
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
    memory = ConversationBufferMemory(chat_memory=history)
    conversation = ConversationChain(llm=llm, memory=memory)

    conversation.predict(input=body["input"])

    return {
        "statusCode": 200,
    }
