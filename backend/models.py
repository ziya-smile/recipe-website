from pydantic import BaseModel, Field


class Recipe(BaseModel):
    id: int
    title: str
    description: str
    image: str | None = None
    ingredients: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    category: str = ""
    cook_time: int | None = None
    difficulty: str = ""


class RecipeCreate(BaseModel):
    title: str
    description: str = ""
    image: str | None = None
    ingredients: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    category: str = ""
    cook_time: int | None = None
    difficulty: str = ""
