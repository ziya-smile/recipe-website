from pydantic import BaseModel, Field


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
