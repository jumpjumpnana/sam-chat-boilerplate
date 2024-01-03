import json
from langchain.memory.chat_message_histories import DynamoDBChatMessageHistory
import os
import boto3
from langchain.llms.sagemaker_endpoint import SagemakerEndpoint, LLMContentHandler
from langchain.chains import ConversationChain
from callback import APIGatewayWebSocketCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from typing import Dict

session_table_name = os.environ["SessionTableName"]
endpoint_name = os.environ["EndpointName"]

session = boto3.session.Session()
sagemaker = session.client("sagemaker-runtime")


class ContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: Dict) -> bytes:
        input_str = json.dumps({"inputs": prompt, "parameters": model_kwargs})
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json[0]["generated_text"]


content_handler = ContentHandler()


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

    llm = SagemakerEndpoint(
        endpoint_name=endpoint_name,
        client=sagemaker,
        model_kwargs={"temperature": 1e-10},
        content_handler=content_handler,
        streaming=True,
        callbacks=[APIGatewayWebSocketCallbackHandler(apigw, connection_id)],
    )

    history = DynamoDBChatMessageHistory(
        table_name=session_table_name,
        session_id=connection_id,
        boto3_session=session,
    )
    memory = ConversationBufferMemory(
        chat_memory=history,
    )

    conversation = ConversationChain(
        llm=llm,
        memory=memory,
    )

    conversation.predict(input=body["input"])

    return {
        "statusCode": 200,
    }
