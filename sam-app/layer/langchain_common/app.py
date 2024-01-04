import json
from langchain.memory.chat_message_histories import DynamoDBChatMessageHistory
from langchain.chains import ConversationChain
from callback import APIGatewayWebSocketCallbackHandler
from langchain.memory import ConversationBufferMemory
from prepare import llm, boto3_session, session_table_name, ai_prefix, prompt


def handler(event, context):
    print(json.dumps(event))
    connection_id = event["requestContext"]["connectionId"]
    body = json.loads(event["body"])

    # set callback handler
    # so that every time the model generates a response,
    # it is sent to the client
    llm.callbacks = [APIGatewayWebSocketCallbackHandler(boto3_session, event)]

    history = DynamoDBChatMessageHistory(
        table_name=session_table_name,
        session_id=connection_id,
        boto3_session=boto3_session,
    )
    memory = ConversationBufferMemory(ai_prefix=ai_prefix, chat_memory=history)
    conversation = ConversationChain(llm=llm, memory=memory)
    conversation.prompt = prompt

    conversation.predict(input=body["input"])

    return {
        "statusCode": 200,
    }
