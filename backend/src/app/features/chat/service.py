import os
from google import genai
from google.genai.types import Content, Part
from src.app.features.recipes.service import list_recipes

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    return _client


SYSTEM_PROMPT = """You are a friendly and knowledgeable cooking assistant for "Fun Recipes", a recipe website.
Your role is to help users with:
- Finding and recommending recipes from the website's collection
- Inventing and suggesting *custom* recipes based on ingredients the user has (provide these directly in the chat!)
- Answering questions about specific recipes, ingredients, substitutions, and techniques
- Giving nutritional information and meal planning tips

Guidelines:
- You have access to the website's recipe collection listed below. Reference them when relevant.
- If a user asks for a custom recipe or what to make with certain ingredients, feel free to invent and write out a great recipe right here in the chat.
- Do not promise that custom recipes are automatically saved to the website database.
- Keep your responses concise and friendly. Use emojis sparingly.
- If a user asks about something completely unrelated to cooking or food, politely redirect them back to food topics."""


async def get_chat_response(messages: list) -> str:
    client = _get_client()

    recipes = list_recipes()
    recipe_lines = []
    for r in recipes:
        ing_list = []
        if r.ingredients:
            for ing in r.ingredients:
                if hasattr(ing, "name"):
                    ing_list.append(ing.name)
                elif isinstance(ing, dict) and "name" in ing:
                    ing_list.append(ing["name"])
                else:
                    ing_list.append(str(ing))
        ingredients_str = ", ".join(ing_list) if ing_list else "N/A"
        recipe_lines.append(
            f"- **{r.title}** (ID: {r.id}): {r.description}. Ingredients: {ingredients_str}."
        )
    recipe_context = "\n".join(recipe_lines) if recipe_lines else "No recipes available yet."

    full_system = (
        SYSTEM_PROMPT
        + "\n\n## Available Recipes on the Website:\n"
        + recipe_context
    )

    if not messages:
        return "Hi! I'm your cooking assistant. How can I help you today? 👨‍🍳"

    history: list[Content] = []
    for msg in messages[:-1]:
        role = "user" if msg.role == "user" else "model"
        history.append(Content(role=role, parts=[Part(text=msg.content)]))

    last_message = messages[-1]

    try:
        chat_session = client.chats.create(
            model="gemini-3.5-flash-lite",
            history=history,
            config={
                "system_instruction": full_system,
                "max_output_tokens": 512,
                "temperature": 0.7,
            },
        )

        response = chat_session.send_message(last_message.content)
        return response.text or "I'm just a cooking assistant, so I can only help you with recipes and food-related questions! 🍳"
    except Exception:
        return "I'm just a cooking assistant, so I can't help with that question. What's cooking in your kitchen today? 🍳"
