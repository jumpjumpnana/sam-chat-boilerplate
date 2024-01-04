import json
from langchain.memory.chat_message_histories import DynamoDBChatMessageHistory
import os
import boto3
from langchain.llms.sagemaker_endpoint import SagemakerEndpoint, LLMContentHandler
from langchain.chains import ConversationChain
from callback import APIGatewayWebSocketCallbackHandler
from langchain.memory import ConversationBufferMemory
from typing import Dict

session_table_name = os.environ["SessionTableName"]
endpoint_name = os.environ["EndpointName"]


class ContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: Dict) -> bytes:
        input_str = json.dumps({"inputs": prompt, "parameters": model_kwargs})
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json[0]["generated_text"]


session = boto3.session.Session()
sagemaker = session.client("sagemaker-runtime")
llm = SagemakerEndpoint(
    endpoint_name=endpoint_name,
    client=sagemaker,
    model_kwargs={"temperature": 1e-10},
    content_handler=ContentHandler(),
    streaming=True,
)


# TODO: move the common handler to layer
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
