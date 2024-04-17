
import os
import base64

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
    AIMessagePromptTemplate,
    PromptTemplate
)
from langchain.llms.base import LLM
from callback import StreamingAPIGatewayWebSocketCallbackHandler


from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.schema import messages_to_dict

from characterdao import (
    CharacterDefinition,
    save_character_definition,
    update_character_definition,
    delete_character_definition,
    get_character_definition
)



def decode_base64_to_string(encoded_string):
    # 将编码后的字符串转换为字节
    bytes_to_decode = encoded_string.encode('utf-8')

    # 对字节进行Base64解码
    decoded_bytes = base64.b64decode(bytes_to_decode)

    # 将解码后的字节转换回字符串
    decoded_string = decoded_bytes.decode('utf-8')

    return decoded_string



def chat(
    event: dict,
    llm: LLM,
    boto3_session: Session,
    session_table_name: str,
    cd_table_name: str,
    ai_prefix: str,
    prompt: PromptTemplate,
):
    # print(json.dumps(event))

    # parse event
    domain = event["requestContext"]["domainName"]
    stage = event["requestContext"]["stage"]
    connection_id = event["requestContext"]["connectionId"]
    bodyJson = event["body"]
    bd = json.dumps(bodyJson)
    body = json.loads(bd,strict=False)

    # body = json.loads(event["body"],strict=False)

    db_connect_id = body.get("connection_id")
    inputInfo = body.get("input")
    cdId = body.get("cdId")# CharacterDefinationId
    nickname = body.get("nickname")


    # greeting = body.get("greeting")
    # userInfo = body.get("userInfo")
    # sysStr = body.get("system").strip()
    # systemInfo = decode_base64_to_string(sysStr)
    


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

    history = DynamoDBChatMessageHistory(
        table_name=session_table_name,
        # use connection_id as session_id for simplicity.
        # in production, you should design the session_id yourself
        session_id=db_connect_id,
        # boto3_session=boto3_session,
    )

    # setting defination
    if cdId:
        cd = get_character_definition(boto3_session, cd_table_name, cdId)
        if cd:
            # gen system info
            # Replace the placeholder
            replacements = {
                "{{char}}": cd.cname,
                "{{user}}": nickname
            }
            # replace personality
            personality = "" if cd.personality is None else cd.personality
            if cd.personality != "":
                for placeholder, value in replacements.items():
                    personality = personality.replace(placeholder, value)
                    # print("personality:"+personality)
            # replace scenario
            scenario = "" if cd.scenario is None else cd.scenario
            if cd.scenario != "":
                for placeholder, value in replacements.items():
                    scenario = scenario.replace(placeholder, value)
                    # print("scenario:"+scenario)
           
            systemInfo = "["+cd.cname+"'s profile: "+cd.gender+"],["+cd.cname+"'s persona: "+personality+"],[scenario: "+scenario+"]"
            print(systemInfo)

    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(systemInfo),
        # HumanMessage(content=userInfo,example=True),
        # AIMessage(content=greeting,example=True),

        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template(inputInfo)
    ])
    # memory = ConversationBufferMemory(ai_prefix=ai_prefix,chat_memory=history,return_messages=True)
    memory = ConversationBufferMemory(chat_memory=history,return_messages=True)
    conversation = ConversationChain(llm=llm,memory=memory)
    conversation.prompt = prompt_template

    a = conversation.predict(input=inputInfo)
    print("a:"+a)
    # messages = history.messages
    # print("history:", ', '.join(f"{message.type}: {message.content}" for message in messages))

















    # [SystemMessage(content='You are a professional translator that translate English to Chinese', additional_kwargs={}), HumanMessage(content='Did you eat in this morning', additional_kwargs={}, example=False)]




    # try:
    #         # messages = history.messages
    #         messagesDef = [
    #             ("system", "You are a helpful AI bot. Your name is Lalalala."),
    #             ("user", "Hello, I am Bob"),
    #             ("ai", "I'm Nana")
    #         ]

    #         messagesDef = messages_to_dict(messagesDef)
    #         # print("messagesDict:", ', '.join(f"{message['type']}: {message['content']}" for message in messagesDict))

    #         history.table.put_item(
    #             Item={"SessionId": db_connect_id, "History": messagesDef}
    #         )
    #     except Exception as e:
    #         print(e)

     # prompt_template = PromptTemplate(input_variables=["history", "system"], template=body["input"]["system"])

    # prompt_template = SystemMessagePromptTemplate.from_template(body["input"]["system"])
    # prompt_template = PromptTemplate.from_template(body["input"]["human"]).partial(system=body["input"]["system"])








