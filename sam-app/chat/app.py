import json
from langchain.memory.chat_message_histories import DynamoDBChatMessageHistory
import os
import boto3
from langchain.llms.bedrock import Bedrock
from langchain.chains import ConversationChain
from callback import APIGatewayWebSocketCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate


session_table_name = os.environ["SessionTableName"]

session = boto3.session.Session()

claude_prompt = PromptTemplate.from_template(
    """
{history}

Human: {input}

Assistant:
"""
)


def handler(event, context):
    print(json.dumps(event))
    domain = event["requestContext"]["domainName"]
    stage = event["requestContext"]["stage"]
    connection_id = event["requestContext"]["connectionId"]
    body = json.loads(event["body"])

    apigw = session.client(
        "apigatewaymanagementapi",
        endpoint_url=f"https://{domain}/{stage}",
    )

    llm = Bedrock(
        model_id="anthropic.claude-v2:1",
        streaming=True,
        callbacks=[APIGatewayWebSocketCallbackHandler(apigw, connection_id)],
    )

    history = DynamoDBChatMessageHistory(
        table_name=session_table_name,
        session_id=connection_id,
        boto3_session=session,
    )
    memory = ConversationBufferMemory(
        ai_prefix="Assistant",
        chat_memory=history,
    )

    conversation = ConversationChain(
        llm=llm,
        memory=memory,
    )
    conversation.prompt = claude_prompt

    conversation.predict(input=body["input"])

    return {
        "statusCode": 200,
    }
