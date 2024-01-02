import json
from langchain.memory.chat_message_histories import DynamoDBChatMessageHistory
import os
import boto3
from langchain.llms.bedrock import Bedrock
from langchain.chains import ConversationChain
from callback import APIGatewayWebSocketCallbackHandler
from langchain.prompts import PromptTemplate


session_table_name = os.environ["SessionTableName"]

session = boto3.session.Session()
apigw = session.client("apigatewaymanagementapi")

claude_prompt = PromptTemplate.from_template(
    """

Human: The following is a friendly conversation between a human and an AI.
The AI is talkative and provides lots of specific details from its context. If the AI does not know
the answer to a question, it truthfully says it does not know.

Current conversation:
<conversation_history>
{history}
</conversation_history>

Here is the human's next reply:
<human_reply>
{input}
</human_reply>

Assistant:
"""
)


def handler(event, context):
    print(json.dumps(event))

    body = json.loads(event["body"])

    connection_id = event["requestContext"]["connectionId"]

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

    conversation = ConversationChain(llm=llm, memory=history)
    conversation.prompt = claude_prompt

    conversation.predict(input=body["input"])

    return {
        "statusCode": 200,
    }
