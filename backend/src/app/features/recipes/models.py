from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Text, JSON, LargeBinary

from src.app.core.database import Base


class Ingredient(BaseModel):
    amount: str | float | int | None = None
    unit: str | None = None
    name: str


class Recipe(BaseModel):
    id: int
    title: str
    description: str
    image: str | None = None
    ingredients: list[Ingredient | str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)


class RecipeCreate(BaseModel):
    title: str
    description: str = ""
    image: str | None = None
    ingredients: list[Ingredient | str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)


class RecipeRecord(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False, default="")
    image = Column(Text, nullable=True)
    ingredients = Column(JSON, nullable=False, default=list)
    steps = Column(JSON, nullable=False, default=list)

    def to_pydantic(self) -> Recipe:
        raw_ings = self.ingredients or []
        parsed_ings = []
        for item in raw_ings:
            if isinstance(item, dict):
                parsed_ings.append(
                    Ingredient(
                        amount=item.get("amount"),
                        unit=item.get("unit"),
                        name=item.get("name", str(item)),
                    )
                )
            else:
                parsed_ings.append(item)
        return Recipe(
            id=self.id,
            title=self.title,
            description=self.description or "",
            image=self.image,
            ingredients=parsed_ings,
            steps=list(self.steps or []),
        )


class ImageRecord(Base):
    __tablename__ = "recipe_images"

    filename = Column(String(255), primary_key=True)
    content_type = Column(String(100), nullable=False, default="application/octet-stream")
    data = Column(LargeBinary, nullable=False)
