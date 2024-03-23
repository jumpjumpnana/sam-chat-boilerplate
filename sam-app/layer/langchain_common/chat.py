
import os

import json
from boto3 import Session
from langchain.memory import DynamoDBChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain,LLMChain
from langchain_core.messages import (
    SystemMessage
) 
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate,
    PromptTemplate
)
from langchain.llms.base import LLM
# from callback import StreamingAPIGatewayWebSocketCallbackHandler
from deepinfracallback import StreamingAPIGatewayWebSocketCallbackHandler


from langchain.llms import DeepInfra
from langchain_community.chat_models import ChatDeepInfra
from langchain_core.messages import HumanMessage, SystemMessage




def chat(
    event: dict,
    llm: LLM,
    boto3_session: Session,
    session_table_name: str,
    ai_prefix: str,
    prompt: PromptTemplate,
):
    # print(json.dumps(event))

    # parse event
    domain = event["requestContext"]["domainName"]
    stage = event["requestContext"]["stage"]
    connection_id = event["requestContext"]["connectionId"]
    body = json.loads(event["body"],strict=False)
    # body = json.loads(event["body"])

    db_connect_id = body["connection_id"]
    print("db_connect_id:"+db_connect_id)

    # set callback handler
    # so that every time the model generates a chunk of response,
    # it is sent to the client
    callback = StreamingAPIGatewayWebSocketCallbackHandler(
        boto3_session,
        # see https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-how-to-call-websocket-api-connections.html
        f"https://{domain}/{stage}",
        connection_id,
        on_token=lambda t: json.dumps({"kind": "token", "chunk": t}),
        on_end=lambda: json.dumps({"kind": "end"}),
        on_err=lambda e: json.dumps({"kind": "error"}),
    )
    llm.callbacks = [callback]

    # chat_memory = DynamoDBChatMessageHistory(
    #     table_name=session_table_name,
    #     # use connection_id as session_id for simplicity.
    #     # in production, you should design the session_id yourself
    #     session_id=db_connect_id,
    #     boto3_session=boto3_session,
    # )
    # print("History"+chat_memory)

    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(body["input"]["system"]),
        HumanMessagePromptTemplate.from_template(body["input"]["human"]),
        # ("system", "Character: Mika. In this situation, respond as Mika would and follow Mika's persona. Persona: Mika is a middle school teacher in Beijing China. She like to say OMG on every sentence."),
        # ("user", "what's your name"),
        # # MessagesPlaceholder(variable_name="history"),
        # # HumanMessagePromptTemplate.from_template(body["input"]["human"])
    ])

    # memory = ConversationBufferMemory(ai_prefix=ai_prefix)
    conversation = ConversationChain(llm=llm)
    conversation.prompt = prompt_template

    a = conversation.predict(input=body["input"]["human"])
    print("a:"+a)



   





     # prompt_template = PromptTemplate(input_variables=["history", "system"], template=body["input"]["system"])

    # prompt_template = SystemMessagePromptTemplate.from_template(body["input"]["system"])
    # prompt_template = PromptTemplate.from_template(body["input"]["human"]).partial(system=body["input"]["system"])


    # system_message = SystemMessage(content=body["input"]["system"])
    # prompt_template = ChatPromptTemplate(messages=[system_message])
     # conversation = ConversationChain(
    #     llm=llm, 
    #     verbose=True,
    #     memory=memory
    # )
       
    # conversation.predict(input="what is your name")
    # conversation.from_template = SystemMessagePromptTemplate.from_template(body["input"]["system"])


    #stream=True,
    #temperature=0.7,
    # max_tokens =200,



      # prompttest =  PromptTemplate.from_template("{ \"messages\": [ { \"role\": \"system\", \"content\": \"Character: Mika. In this situation, respond as Mika would and follow Mika's persona. Persona: Mika is a middle school teacher in Beijing China. She like to say OMG on every sentence.\" }, { \"role\": \"user\", \"content\": \"what is your name\" } ] }")
    # prompttest = ChatPromptTemplate.from_messages([
        # {
        #   "role": "system",
        #   "content": "Character: Mika. In this situation, respond as Mika would and follow Mika's persona. Persona: Mika is a middle school teacher in Beijing China. She like to say OMG on every sentence."
        # }
        # {
        #   "role": "user",
        #   "content": "what is your name"
        # }
    # ])



# { "messages": [
#     {
#       "role": "system",
#       "content": "Character: Mika. In this situation, respond as Mika would and follow Mika's persona. Persona: Mika is a middle school teacher in Beijing China. She like to say OMG on every sentence."
#     }
#     {
#       "role": "user",
#       "content": "what is your name"
#     }
#   ]
# } 



# prompttest = [
#         f"{role}: {content}"
#         for role, content in (
#             ("system", body["input"]["system"]),
#             ("user", body["input"]["human"])
#         )
#     ]
#     print("system:"+body["input"]["system"])
#     print("human:"+body["input"]["human"])

#     example_prompt = PromptTemplate(
#         input_variables=[""],
#         template=prompttest,
#     )


   







