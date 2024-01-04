import json
import os
import boto3
from langchain.llms.sagemaker_endpoint import SagemakerEndpoint, LLMContentHandler
from langchain.chains.conversation.prompt import PROMPT
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


boto3_session = boto3.session.Session()
sagemaker = boto3_session.client("sagemaker-runtime")
llm = SagemakerEndpoint(
    endpoint_name=endpoint_name,
    client=sagemaker,
    model_kwargs={"temperature": 1e-10},
    content_handler=ContentHandler(),
    streaming=True,
)
ai_prefix = "AI"  # use default
prompt = PROMPT
