from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, List, Callable
from boto3 import Session
from langchain_core.callbacks.base import BaseCallbackHandler

if TYPE_CHECKING:
    from langchain_core.agents import AgentAction, AgentFinish
    from langchain_core.messages import BaseMessage
    from langchain_core.outputs import LLMResult


class APIGatewayWebSocketCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming. Only works with LLMs that support streaming."""

    def __init__(
        self,
        boto3_session: Session,
        endpoint_url: str,
        connection_id: str,
        formatter: Callable[[str], str] = lambda x: x,
    ):
        """
        Initialize callback handler
        with boto3 session and api gateway websocket event.
        """
        self.connection_id = connection_id
        self.apigw = boto3_session.client(
            "apigatewaymanagementapi",
            endpoint_url=endpoint_url,
        )
        self.formatter = formatter
        super().__init__()

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        self.apigw.post_to_connection(
            ConnectionId=self.connection_id,
            Data=self.formatter(token),
        )

    def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[BaseMessage]],
        **kwargs: Any,
    ) -> None:
        """Run when LLM starts running."""
