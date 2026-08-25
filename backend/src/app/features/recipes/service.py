import json
from threading import Lock

from src.app.core.database import get_session_factory, data_dir, reset as database_reset, uploads_dir, get_db_url, is_postgres, get_db_type
from src.app.features.recipes.models import Recipe, RecipeCreate, RecipeRecord, ImageRecord, Ingredient

_lock = Lock()

def reset() -> None:
    database_reset()

SEED_RECIPES: list[Recipe] = []


def _maybe_seed(session_factory):
    with session_factory() as session:
        count = session.query(RecipeRecord).count()
        if count == 0:
            if SEED_RECIPES:
                for recipe in SEED_RECIPES:
                    record = RecipeRecord(
                        title=recipe.title,
                        description=recipe.description,
                        image=recipe.image,
                        ingredients=[
                            i.dict() if hasattr(i, "dict") else i
                            for i in recipe.ingredients
                        ],
                        steps=recipe.steps,
                    )
                    session.add(record)
                session.commit()
            else:
                json_path = data_dir() / "recipes.json"
                if json_path.exists():
                    try:
                        raw = json.loads(json_path.read_text(encoding="utf-8"))
                        for item in raw:
                            record = RecipeRecord(
                                title=item.get("title", ""),
                                description=item.get("description", ""),
                                image=item.get("image"),
                                ingredients=item.get("ingredients", []),
                                steps=item.get("steps", []),
                            )
                            session.add(record)
                        session.commit()
                    except Exception:
                        pass


def list_recipes() -> list[Recipe]:
    with _lock:
        session_factory = get_session_factory(seed_func=_maybe_seed)
        with session_factory() as session:
            records = session.query(RecipeRecord).order_by(RecipeRecord.id.asc()).all()
            return [record.to_pydantic() for record in records]


def get_recipe(recipe_id: int) -> Recipe | None:
    with _lock:
        session_factory = get_session_factory(seed_func=_maybe_seed)
        with session_factory() as session:
            record = session.query(RecipeRecord).filter(RecipeRecord.id == recipe_id).first()
            return record.to_pydantic() if record else None


def create_recipe(payload: RecipeCreate) -> Recipe:
    with _lock:
        session_factory = get_session_factory(seed_func=_maybe_seed)
        with session_factory() as session:
            ings = [
                i.dict() if hasattr(i, "dict") else i
                for i in payload.ingredients
            ]
            record = RecipeRecord(
                title=payload.title,
                description=payload.description,
                image=payload.image,
                ingredients=ings,
                steps=payload.steps,
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return record.to_pydantic()


def update_recipe(recipe_id: int, payload: RecipeCreate) -> Recipe | None:
    with _lock:
        session_factory = get_session_factory(seed_func=_maybe_seed)
        with session_factory() as session:
            record = session.query(RecipeRecord).filter(RecipeRecord.id == recipe_id).first()
            if not record:
                return None
            record.title = payload.title
            record.description = payload.description
            if payload.image is not None:
                record.image = payload.image
            record.ingredients = [
                i.dict() if hasattr(i, "dict") else i
                for i in payload.ingredients
            ]
            record.steps = payload.steps
            session.commit()
            session.refresh(record)
            return record.to_pydantic()


def save_image(filename: str, content_type: str, data: bytes) -> None:
    with _lock:
        session_factory = get_session_factory(seed_func=_maybe_seed)
        with session_factory() as session:
            session.add(
                ImageRecord(filename=filename, content_type=content_type, data=data)
            )
            session.commit()


def get_image(filename: str) -> tuple[str, bytes] | None:
    with _lock:
        session_factory = get_session_factory(seed_func=_maybe_seed)
        with session_factory() as session:
            record = session.get(ImageRecord, filename)
            if record is None:
                return None
            return record.content_type, record.data


def delete_recipe(recipe_id: int) -> bool:
    with _lock:
        session_factory = get_session_factory(seed_func=_maybe_seed)
        with session_factory() as session:
            record = session.query(RecipeRecord).filter(RecipeRecord.id == recipe_id).first()
            if record:
                session.delete(record)
                session.commit()
                return True
            return False
