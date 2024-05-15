
import os
import base64
import requests
import time
from datetime import datetime, timedelta

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
    get_character_definition,
    save_character_definition,
    update_character_definition,
    delete_character_definition
)

from CharacterMessagesDao import (
    CharacterMessages,
    save_character_messages,
    get_character_messages,
    update_character_messages
)
from UserMessagesDao import (
    UserMessages,
    save_user_messages,
    has_sufficient_messages
)

from common import (
    get_date_time,
    decode_base64_to_string
)



def chat(
    event: dict,
    llm: LLM,
    boto3_session: Session,
    session_table_name: str,
    cd_table_name: str,
    cm_table_name: str,
    um_table_name: str,
    ai_prefix: str,
    prompt: PromptTemplate,
):
    # print(event)

    # parse event
    domain = event["requestContext"]["domainName"]
    stage = event["requestContext"]["stage"]
    connection_id = event["requestContext"]["connectionId"]
    bodyJson = event["body"]

    dataBase = bodyJson.get("data")
    dataStr = decode_base64_to_string(dataBase)
    data = json.loads(dataStr)

    db_connect_id = data.get("connection_id")
    inputInfo = data.get("input")
    characterId = data.get("cdId")# CharacterId
    nickname = data.get("nickname")
    # token = data.get("token")
    uid = data.get("uid")


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
        # on_err=lambda e, message=None: json.dumps({"kind": "error", "message": message or str(e) or "An error occurred"}),
        on_err=lambda e,message=None,error_code=None: json.dumps({
                "kind": "error",
                "message": message or str(e) or "An error occurred", 
                "error_code": error_code})
    )


    # if not uid:
    #     try:
    #         raise ValueError("User identifier (uid) not found in the request.")
    #     except Exception as e:
    #         custom_message = "User identifier (uid) not found in the request."
    #         error_code = -1
    #         callback.on_llm_error(error=e, message=custom_message, error_code=error_code)
    #     return

    # 判断消息数是否足够扣除
    can_deduct = has_sufficient_messages(boto3_session, um_table_name,uid ,1)
    if not can_deduct:
        try:
            raise ValueError("Insufficient messages. Please recharge to continue.")
        except Exception as e:
            custom_message = "Insufficient messages. Please recharge to continue."
            error_code = -1
            callback.on_llm_error(error=e, message=custom_message, error_code=error_code)
        return


    llm.callbacks = [callback]


    history = DynamoDBChatMessageHistory(
        table_name=session_table_name,
        # use connection_id as session_id for simplicity.
        # in production, you should design the session_id yourself
        session_id=db_connect_id,
        # boto3_session=boto3_session,
    )

    systemInfo = ""
    greeting = ""
    # setting defination
    cd = get_character_definition(boto3_session, cd_table_name, characterId)
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
        # print("systemInfo:"+systemInfo)
        greeting = cd.greeting
        # print("greeting:"+greeting)

    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(systemInfo),
        # HumanMessage(content=userInfo,example=True),
        AIMessage(content=greeting,example=True),

        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template(inputInfo)
    ])
    # memory = ConversationBufferMemory(ai_prefix=ai_prefix,chat_memory=history,return_messages=True)
    memory = ConversationBufferMemory(chat_memory=history,return_messages=True)
    conversation = ConversationChain(llm=llm,memory=memory)
    conversation.prompt = prompt_template
   

    a = conversation.predict(input=inputInfo)
    # print("a:"+a)

    # 对话量计数
    update_character_messages(boto3_session, cm_table_name, characterId)
   






    # # 同步消息
    # # 定义请求的 URL
    # url = 'http://47.251.23.202:8080/ucenter/endChat'

    # json_data = {
    #     'characterId': characterId
    # }
    # # 发送 GET 请求
    # response = requests.post(url,json=json_data)

    # # 检查响应状态码
    # if response.status_code == 200:
    #     # 打印响应内容
    #     print(response.text)
    # else:
    #     # 打印错误信息
    #     print('Error:', response.status_code)

    










