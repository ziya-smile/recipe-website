from typing import Annotated
from fastapi import APIRouter, Body
from pydantic import BaseModel

from src.app.features.chat.service import get_chat_response

router = APIRouter()


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class ChatResponse(BaseModel):
    reply: str


@router.post("/api/chat", response_model=ChatResponse)
async def chat(payload: Annotated[ChatRequest, Body()]) -> ChatResponse:
    reply = await get_chat_response(payload.messages)
    return ChatResponse(reply=reply)
