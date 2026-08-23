import os
from typing import Annotated

from fastapi import APIRouter, Body
from google import genai
from google.genai.types import Content, Part
from pydantic import BaseModel

from store import list_recipes as store_list_recipes

router = APIRouter()

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    return _client


SYSTEM_PROMPT = """You are a friendly and knowledgeable cooking assistant for "Fun Recipes", a recipe website.
Your role is to help users with:
- Finding recipes that match their interests or dietary needs
- Answering questions about specific recipes (ingredients, steps, substitutions, tips)
- Providing cooking advice and techniques
- Suggesting what to cook based on available ingredients
- Giving nutritional information and meal planning tips

You have access to the website's recipe collection. When discussing recipes from the collection, be specific and helpful.
Keep your responses concise and friendly. Use emojis sparingly to keep things warm.
If a user asks about something unrelated to cooking or recipes, politely redirect them back to food topics."""


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class ChatResponse(BaseModel):
    reply: str


@router.post("/api/chat", response_model=ChatResponse)
async def chat(payload: Annotated[ChatRequest, Body()]) -> ChatResponse:
    client = _get_client()

    # Build recipe context for the system prompt
    recipes = store_list_recipes()
    recipe_lines = []
    for r in recipes:
        ingredients_str = ", ".join(r.ingredients) if r.ingredients else "N/A"
        recipe_lines.append(
            f"- **{r.title}** (ID: {r.id}): {r.description}. Ingredients: {ingredients_str}."
        )
    recipe_context = "\n".join(recipe_lines) if recipe_lines else "No recipes available yet."

    full_system = (
        SYSTEM_PROMPT
        + "\n\n## Available Recipes on the Website:\n"
        + recipe_context
    )

    # Convert our message history to the Gemini history format
    messages = payload.messages

    if not messages:
        return ChatResponse(reply="Hi! I'm your cooking assistant. How can I help you today? 👨‍🍳")

    # Build history (all messages except the last user message)
    history: list[Content] = []
    for msg in messages[:-1]:
        role = "user" if msg.role == "user" else "model"
        history.append(Content(role=role, parts=[Part(text=msg.content)]))

    last_message = messages[-1]

    chat_session = client.chats.create(
        model="gemini-3.7-flash",
        history=history,
        config={
            "system_instruction": full_system,
            "max_output_tokens": 512,
            "temperature": 0.7,
        },
    )

    response = chat_session.send_message(last_message.content)
    reply_text = response.text or "Sorry, I couldn't generate a response. Please try again."

    return ChatResponse(reply=reply_text)
