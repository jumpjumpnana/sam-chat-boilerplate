import json
import os
import boto3

# environment variables
model_id = os.environ.get("ModelId", "anthropic.claude-v2:1")
session_table_name = os.environ["SessionTableName"]

# init clients outside of handler
session = boto3.session.Session()
ddb = session.client("dynamodb")
bedrock = session.client("bedrock-runtime")


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

    # TODO: get chat history from ddb

    res = bedrock.invoke_model_with_response_stream(
        modelId=model_id,
        body=json.dumps(
            {
                "prompt": f"\n\nHuman: { body['input'] }\n\nAssistant:",
                "max_tokens_to_sample": 300,
                "temperature": 0.5,
                "top_k": 250,
                "top_p": 1,
                "stop_sequences": ["\n\nHuman:"],
                "anthropic_version": "bedrock-2023-05-31",
            }
        ),
    )

    # stream response to client
    for data in res["body"]:
        # print(data)
        apigw.post_to_connection(
            ConnectionId=connection_id,
            Data=json.loads(data["chunk"]["bytes"])["completion"],
        )

    # TODO: write history to ddb

    return {
        "statusCode": 200,
    }
