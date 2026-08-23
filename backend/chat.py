import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from store import list_recipes

router = APIRouter(prefix="/api/chat")

GEMINI_MODEL = "gemini-3.6-flash"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


@router.post("")
def chat(req: ChatRequest):
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="AI chat is not configured. Set GEMINI_API_KEY to enable it.",
        )

    recipes = list_recipes()
    if recipes:
        catalog = "\n".join(
            f"- #{r.id}: {r.title}"
            f" (category: {r.category or 'Uncategorized'},"
            f" cook time: {r.cook_time or '?'} min,"
            f" difficulty: {r.difficulty or 'easy'})"
            f" — {r.description}"
            for r in recipes
        )
    else:
        catalog = "No recipes have been added to the site yet."

    system_prompt = (
        "You are the Fun Recipes assistant, a friendly cooking coach embedded in a "
        "recipe website. Help users in two ways: (1) recommend recipes from the site's "
        "catalog based on what they're craving or the ingredients they have, and "
        "(2) give general cooking advice — tips, substitutions, techniques, and timing.\n\n"
        f"Current recipe catalog:\n{catalog}\n\n"
        "When you recommend a recipe from the catalog, mention its title and ID "
        "(e.g. \"Try #3 — Lemon Garlic Salmon\"). If nothing in the catalog fits, "
        "give general advice and suggest they ask an admin to add the recipe. "
        "Keep responses concise, warm, and practical. Use short paragraphs or "
        "bullet points. Never invent recipe IDs that aren't in the catalog."
    )

    contents = [
        {"role": msg.role, "parts": [{"text": msg.content}]} for msg in req.history
    ]
    contents.append({"role": "user", "parts": [{"text": req.message}]})

    payload = json.dumps(
        {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": contents,
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 800},
        }
    ).encode()

    request = Request(
        f"{GEMINI_URL}?key={api_key}",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )

    try:
        with urlopen(request, timeout=30) as resp:
            data = json.loads(resp.read())
    except HTTPError as exc:
        detail = f"Gemini API error (status {exc.code})"
        try:
            err_body = json.loads(exc.read())
            detail = err_body.get("error", {}).get("message", detail)
        except Exception:
            pass
        raise HTTPException(status_code=502, detail=detail)
    except URLError:
        raise HTTPException(
            status_code=502, detail="Could not reach the AI service."
        )

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        text = "Sorry, I couldn't generate a response. Please try again."

    return {"reply": text}
